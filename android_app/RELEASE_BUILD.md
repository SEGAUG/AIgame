# Immortal Demo Android 打包说明

## 1) 生成签名证书（只做一次）

在 `android_app` 目录执行：

```powershell
keytool -genkeypair -v -keystore release.keystore -alias immortal -keyalg RSA -keysize 2048 -validity 36500
```

## 2) 配置签名参数

```powershell
Copy-Item .\keystore.properties.example .\keystore.properties
```

编辑 `keystore.properties`，填入你的密码和别名。

## 3) 一键构建 Release APK

```powershell
.\build_release.ps1
```

输出文件：

`app\build\outputs\apk\release\app-release.apk`

## 4) 安装到手机测试

```powershell
& "C:\Users\jinhui\AppData\Local\Android\Sdk\platform-tools\adb.exe" install -r ".\app\build\outputs\apk\release\app-release.apk"
```
