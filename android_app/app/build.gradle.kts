import java.io.FileInputStream
import java.io.File
import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val keystoreProps = Properties()
val keystoreFile = rootProject.file("keystore.properties")
if (keystoreFile.exists()) {
    FileInputStream(keystoreFile).use { keystoreProps.load(it) }
}

fun readSigningValue(key: String): String? {
    return keystoreProps.getProperty(key)
        ?: providers.gradleProperty(key).orNull
        ?: System.getenv(key.uppercase())
}

val releaseStoreFile = readSigningValue("storeFile")
val releaseStorePassword = readSigningValue("storePassword")
val releaseKeyAlias = readSigningValue("keyAlias")
val releaseKeyPassword = readSigningValue("keyPassword") ?: releaseStorePassword
val hasReleaseSigning = !releaseStoreFile.isNullOrBlank()
    && !releaseStorePassword.isNullOrBlank()
    && !releaseKeyAlias.isNullOrBlank()
    && !releaseKeyPassword.isNullOrBlank()
val includeModels = providers.gradleProperty("includeModels")
    .orNull
    ?.toBooleanStrictOrNull()
    ?: true

android {
    namespace = "com.jinhui.immortaldemo"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.jinhui.immortaldemo"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        ndk {
            abiFilters += listOf("arm64-v8a")
        }

        externalNativeBuild {
            cmake {
                cppFlags += "-std=c++17"
            }
        }
    }

    signingConfigs {
        create("release") {
            if (hasReleaseSigning) {
                val f = File(releaseStoreFile!!)
                storeFile = if (f.isAbsolute) f else rootProject.file(releaseStoreFile)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            isDebuggable = false
            signingConfig = if (hasReleaseSigning) {
                signingConfigs.getByName("release")
            } else {
                // fallback to debug signing so CI/local can still produce installable release apk
                signingConfigs.getByName("debug")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    sourceSets {
        getByName("main") {
            if (includeModels) {
                // package local GGUF models into APK assets for offline NPC inference
                assets.srcDirs("src/main/assets", "../../models")
            } else {
                // lean build: do not package local model files
                assets.srcDirs("src/main/assets")
            }
        }
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
        }
    }

    androidResources {
        noCompress += "gguf"
    }
}

if (!hasReleaseSigning) {
    println("Warning: keystore.properties not fully configured. release apk will use debug signing.")
}
if (!includeModels) {
    println("Info: includeModels=false, model assets are excluded from APK.")
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
}
