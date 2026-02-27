package com.jinhui.immortaldemo.core

fun interface NpcInferenceProvider {
    fun generate(prompt: String): String?
}
