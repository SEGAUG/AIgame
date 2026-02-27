#include <jni.h>
#include <android/log.h>
#include <algorithm>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#include "llama.h"

#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, "immortal_llama", __VA_ARGS__)
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "immortal_llama", __VA_ARGS__)

namespace {

std::mutex g_mutex;
bool g_backend_inited = false;
llama_model * g_model = nullptr;
llama_context * g_ctx = nullptr;
int g_ctx_size = 1024;
int g_threads = 4;

static void clear_model_locked() {
    if (g_ctx != nullptr) {
        llama_free(g_ctx);
        g_ctx = nullptr;
    }
    if (g_model != nullptr) {
        llama_model_free(g_model);
        g_model = nullptr;
    }
}

static std::string jstring_to_string(JNIEnv * env, jstring value) {
    if (value == nullptr) {
        return "";
    }
    const char * chars = env->GetStringUTFChars(value, nullptr);
    if (chars == nullptr) {
        return "";
    }
    std::string out(chars);
    env->ReleaseStringUTFChars(value, chars);
    return out;
}

static int resolve_threads(int requested) {
    if (requested > 0) {
        return std::clamp(requested, 1, 8);
    }
    const unsigned int hc = std::thread::hardware_concurrency();
    if (hc <= 2) {
        return 1;
    }
    return std::clamp(static_cast<int>(hc) - 1, 2, 8);
}

static std::string generate_locked(
        const std::string & prompt,
        const int n_predict,
        const float temp,
        const float top_p
) {
    if (g_model == nullptr || g_ctx == nullptr) {
        return "";
    }
    const llama_vocab * vocab = llama_model_get_vocab(g_model);
    if (vocab == nullptr) {
        return "";
    }

    int n_prompt = -llama_tokenize(vocab, prompt.c_str(), static_cast<int32_t>(prompt.size()), nullptr, 0, true, true);
    if (n_prompt <= 0) {
        return "";
    }
    if (n_prompt >= g_ctx_size - 8) {
        // keep some room for generation tokens
        return "";
    }

    std::vector<llama_token> prompt_tokens(static_cast<size_t>(n_prompt));
    if (llama_tokenize(
            vocab,
            prompt.c_str(),
            static_cast<int32_t>(prompt.size()),
            prompt_tokens.data(),
            static_cast<int32_t>(prompt_tokens.size()),
            true,
            true) < 0) {
        return "";
    }

    llama_memory_clear(llama_get_memory(g_ctx), false);
    llama_batch batch = llama_batch_get_one(prompt_tokens.data(), static_cast<int32_t>(prompt_tokens.size()));
    if (llama_decode(g_ctx, batch) != 0) {
        return "";
    }

    auto sparams = llama_sampler_chain_default_params();
    llama_sampler * smpl = llama_sampler_chain_init(sparams);
    if (smpl == nullptr) {
        return "";
    }

    if (temp <= 0.01f) {
        llama_sampler_chain_add(smpl, llama_sampler_init_greedy());
    } else {
        llama_sampler_chain_add(smpl, llama_sampler_init_top_k(40));
        llama_sampler_chain_add(smpl, llama_sampler_init_top_p(std::clamp(top_p, 0.1f, 1.0f), 1));
        llama_sampler_chain_add(smpl, llama_sampler_init_temp(std::max(temp, 0.1f)));
        llama_sampler_chain_add(smpl, llama_sampler_init_dist(1337));
    }

    std::string out;
    out.reserve(static_cast<size_t>(n_predict) * 3);
    for (int i = 0; i < n_predict; ++i) {
        llama_token token = llama_sampler_sample(smpl, g_ctx, -1);
        if (llama_vocab_is_eog(vocab, token)) {
            break;
        }

        char piece[256];
        const int n = llama_token_to_piece(vocab, token, piece, sizeof(piece), 0, true);
        if (n <= 0) {
            break;
        }
        out.append(piece, static_cast<size_t>(n));

        batch = llama_batch_get_one(&token, 1);
        if (llama_decode(g_ctx, batch) != 0) {
            break;
        }
    }

    llama_sampler_free(smpl);
    return out;
}

} // namespace

extern "C" JNIEXPORT jboolean JNICALL
Java_com_jinhui_immortaldemo_core_LocalLlamaJni_nativeInitBackend(
        JNIEnv * env,
        jobject /* thiz */,
        jstring /* nativeLibDir */) {
    std::lock_guard<std::mutex> lock(g_mutex);
    if (!g_backend_inited) {
        llama_backend_init();
        g_backend_inited = true;
        LOGI("llama backend initialized");
    }
    return JNI_TRUE;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_jinhui_immortaldemo_core_LocalLlamaJni_nativeLoadModel(
        JNIEnv * env,
        jobject /* thiz */,
        jstring modelPath,
        jint nCtx,
        jint nThreads) {
    std::lock_guard<std::mutex> lock(g_mutex);
    if (!g_backend_inited) {
        llama_backend_init();
        g_backend_inited = true;
    }

    clear_model_locked();

    const std::string path = jstring_to_string(env, modelPath);
    if (path.empty()) {
        LOGE("empty model path");
        return JNI_FALSE;
    }

    llama_model_params model_params = llama_model_default_params();
    model_params.n_gpu_layers = 0;
    g_model = llama_model_load_from_file(path.c_str(), model_params);
    if (g_model == nullptr) {
        LOGE("failed to load model: %s", path.c_str());
        return JNI_FALSE;
    }

    g_ctx_size = std::max(512, static_cast<int>(nCtx));
    g_threads = resolve_threads(static_cast<int>(nThreads));

    llama_context_params ctx_params = llama_context_default_params();
    ctx_params.n_ctx = static_cast<uint32_t>(g_ctx_size);
    ctx_params.n_batch = static_cast<uint32_t>(g_ctx_size);
    ctx_params.n_threads = g_threads;
    ctx_params.n_threads_batch = g_threads;

    g_ctx = llama_init_from_model(g_model, ctx_params);
    if (g_ctx == nullptr) {
        LOGE("failed to create context");
        clear_model_locked();
        return JNI_FALSE;
    }
    LOGI("model loaded, ctx=%d, threads=%d", g_ctx_size, g_threads);
    return JNI_TRUE;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_jinhui_immortaldemo_core_LocalLlamaJni_nativeGenerate(
        JNIEnv * env,
        jobject /* thiz */,
        jstring prompt,
        jint nPredict,
        jfloat temp,
        jfloat topP) {
    std::lock_guard<std::mutex> lock(g_mutex);
    if (g_model == nullptr || g_ctx == nullptr) {
        return nullptr;
    }
    const std::string prompt_str = jstring_to_string(env, prompt);
    if (prompt_str.empty()) {
        return nullptr;
    }

    const int n_predict = std::clamp(static_cast<int>(nPredict), 8, 256);
    const std::string out = generate_locked(prompt_str, n_predict, temp, topP);
    if (out.empty()) {
        return nullptr;
    }
    return env->NewStringUTF(out.c_str());
}

extern "C" JNIEXPORT void JNICALL
Java_com_jinhui_immortaldemo_core_LocalLlamaJni_nativeRelease(
        JNIEnv * /* env */,
        jobject /* thiz */) {
    std::lock_guard<std::mutex> lock(g_mutex);
    clear_model_locked();
    if (g_backend_inited) {
        llama_backend_free();
        g_backend_inited = false;
    }
    LOGI("llama resources released");
}
