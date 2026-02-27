param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Get-PropValue {
    param(
        [Parameter(Mandatory = $true)][string]$File,
        [Parameter(Mandatory = $true)][string]$Key
    )

    $line = Get-Content $File | Where-Object {
        $_ -match "^\s*$Key\s*="
    } | Select-Object -First 1

    if (-not $line) { return "" }
    return ($line -split "=", 2)[1].Trim()
}

function Invoke-Gradle {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $output = & .\gradlew.bat @Args 2>&1 | ForEach-Object { $_.ToString() }
    $output | ForEach-Object { Write-Host $_ }

    $text = $output -join "`n"
    if ($LASTEXITCODE -ne 0 -or $text -match "BUILD FAILED") {
        throw "Gradle failed: gradlew.bat $($Args -join ' ')"
    }
    if ($text -notmatch "BUILD SUCCESSFUL") {
        throw "Gradle finished without success marker."
    }
}

if (-not (Test-Path ".\keystore.properties")) {
    if (Test-Path ".\keystore.properties.example") {
        Write-Host "Missing keystore.properties, found template keystore.properties.example." -ForegroundColor Yellow
        Write-Host "Please copy the template and fill signing values:" -ForegroundColor Yellow
        Write-Host "  Copy-Item .\keystore.properties.example .\keystore.properties"
    } else {
        Write-Host "Missing keystore.properties. Create signing config first." -ForegroundColor Yellow
    }
    throw "Signing config missing, stop build."
}

$storeFile = Get-PropValue -File ".\keystore.properties" -Key "storeFile"
if ($storeFile) {
    $storePath = if ([System.IO.Path]::IsPathRooted($storeFile)) {
        $storeFile
    } else {
        Join-Path $PSScriptRoot $storeFile
    }

    if (-not (Test-Path $storePath)) {
        throw "Keystore not found: $storePath"
    }
}

if ($Clean) {
    Invoke-Gradle -Args @("clean")
}

$apk = ".\app\build\outputs\apk\release\app-release.apk"
if (Test-Path $apk) {
    Remove-Item $apk -Force
}

Invoke-Gradle -Args @("assembleRelease")

if (Test-Path $apk) {
    $f = Get-Item $apk
    Write-Host ""
    Write-Host "Release APK generated:" -ForegroundColor Green
    Write-Host $f.FullName
    Write-Host ("Size: {0:N2} MB" -f ($f.Length / 1MB))
} else {
    throw "Cannot find app-release.apk. Build may have failed."
}
