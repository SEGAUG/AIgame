package com.jinhui.immortaldemo.core

import android.content.Context
import java.io.File

class LocalLlamaProvider(
    context: Context,
    private val modelFileName: String,
    private val nPredict: Int,
    private val nThreads: Int,
    private val nCtx: Int = 1024,
    private val inferTimeoutMs: Int = 12000,
) : NpcInferenceProvider {
    private val appContext = context.applicationContext
    private val lock = Any()

    @Volatile
    private var loaded = false

    override fun generate(prompt: String): String? {
        synchronized(lock) { ensureLoaded() }

        val normalized = prompt.replace("\r", "").trim()
        val promptVariants = listOf(
            normalized.takeLast(900),
            normalized.takeLast(700),
            normalized.takeLast(520),
        ).filter { it.isNotBlank() }.distinct()

        var lastError: Throwable? = null
        for (candidate in promptVariants) {
            val out = runWithTimeout(candidate)
            if (!out.isNullOrBlank()) {
                return out
            }
            if (lastError == null) {
                lastError = IllegalStateException("local model empty output")
            }
        }
        throw IllegalStateException(lastError?.message ?: "local model empty output")
    }

    private fun runWithTimeout(prompt: String): String? {
        var result: String? = null
        var error: Throwable? = null
        val worker = Thread {
            try {
                synchronized(lock) {
                    result = LocalLlamaJni.generate(
                        prompt = prompt,
                        nPredict = nPredict.coerceIn(16, 80),
                        temp = 0.75f,
                        topP = 0.92f,
                    )
                }
            } catch (t: Throwable) {
                error = t
            }
        }
        worker.start()
        worker.join(inferTimeoutMs.toLong())
        if (worker.isAlive) {
            worker.interrupt()
            throw IllegalStateException("local model timeout ${inferTimeoutMs}ms")
        }
        if (error != null) {
            throw IllegalStateException(error?.message ?: "local model inference failed")
        }
        return result?.trim()
    }

    private fun ensureLoaded() {
        if (loaded) return
        if (!LocalLlamaJni.isAvailable()) {
            throw IllegalStateException("jni library not loaded")
        }
        val modelPath = ensureModelFile()
            ?: throw IllegalStateException("model file not found: $modelFileName")
        if (!LocalLlamaJni.initBackend(appContext.applicationInfo.nativeLibraryDir ?: "")) {
            throw IllegalStateException("init backend failed")
        }
        if (!LocalLlamaJni.loadModel(modelPath, nCtx, nThreads)) {
            throw IllegalStateException("load model failed: $modelPath")
        }
        loaded = true
    }

    private fun ensureModelFile(): String? {
        val modelDir = File(appContext.filesDir, "models")
        if (!modelDir.exists()) modelDir.mkdirs()
        val dst = File(modelDir, modelFileName)
        if (dst.exists() && dst.length() > 8L * 1024L * 1024L) {
            return dst.absolutePath
        }

        if (copyAssetIfExists(modelFileName, dst)) return dst.absolutePath
        if (copyAssetIfExists("models/$modelFileName", dst)) return dst.absolutePath

        val external = File("/sdcard/Download/$modelFileName")
        if (external.exists() && external.length() > 8L * 1024L * 1024L) {
            runCatching { external.copyTo(dst, overwrite = true) }
            if (dst.exists() && dst.length() > 8L * 1024L * 1024L) return dst.absolutePath
        }
        return null
    }

    private fun copyAssetIfExists(assetPath: String, dst: File): Boolean {
        return try {
            appContext.assets.open(assetPath).use { input ->
                dst.outputStream().use { output ->
                    input.copyTo(output, bufferSize = 1024 * 1024)
                }
            }
            dst.exists() && dst.length() > 8L * 1024L * 1024L
        } catch (_: Throwable) {
            if (dst.exists() && dst.length() == 0L) {
                dst.delete()
            }
            false
        }
    }
}
