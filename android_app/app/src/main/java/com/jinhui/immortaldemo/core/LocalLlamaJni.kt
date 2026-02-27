package com.jinhui.immortaldemo.core

object LocalLlamaJni {
    private val loaded: Boolean by lazy {
        try {
            System.loadLibrary("immortal_llama")
            true
        } catch (_: UnsatisfiedLinkError) {
            false
        }
    }

    fun isAvailable(): Boolean = loaded

    fun initBackend(nativeLibDir: String): Boolean {
        if (!loaded) return false
        return nativeInitBackend(nativeLibDir)
    }

    fun loadModel(modelPath: String, nCtx: Int = 1024, nThreads: Int = 4): Boolean {
        if (!loaded) return false
        return nativeLoadModel(modelPath, nCtx, nThreads)
    }

    fun generate(prompt: String, nPredict: Int = 64, temp: Float = 0.7f, topP: Float = 0.9f): String? {
        if (!loaded) return null
        return nativeGenerate(prompt, nPredict, temp, topP)
    }

    fun release() {
        if (loaded) {
            nativeRelease()
        }
    }

    private external fun nativeInitBackend(nativeLibDir: String): Boolean
    private external fun nativeLoadModel(modelPath: String, nCtx: Int, nThreads: Int): Boolean
    private external fun nativeGenerate(prompt: String, nPredict: Int, temp: Float, topP: Float): String?
    private external fun nativeRelease()
}
