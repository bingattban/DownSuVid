[app]

# Application title
title = DownSuVid

# Package name
package.name = downsuviid
package.domain = com.downsuviid

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,md

# Version
version = 1.0.0

# Requirements
requirements = python3==3.11.0,hostpython3==3.11.0,kivy==2.2.1,kivymd==1.1.1,yt-dlp==2023.10.13,httpx==0.24.1,aiofiles==23.2.0,Pillow==10.0.0,psutil==5.9.5

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,VIBRATE

# Android API level
android.api = 31
android.minapi = 26
android.ndk = 25b
android.sdk = 31

# Architecture
android.arch = arm64-v8a,armeabi-v7a

# Gradle
android.gradle_dependencies = 'androidx.core:core:1.10.1','androidx.appcompat:appcompat:1.6.1','com.google.android.material:material:1.9.0'

# Services
services = DownloadService:app.services.download.download_service

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Icon
icon.filename = assets/icons/icon.png

# Presplash
presplash.filename = assets/splash/splash.png
presplash.color = #1A237E

# Logging
log_level = 2
logcat_pretty = 1

# Android specific
android.allow_backup = True
android.backup_rules = android_backup_rules.xml
android.entrypoint = org.kivy.android.PythonActivity
android.add_src = 
android.add_resources = 
android.add_jars = 
android.add_aars = 

# Python for android
p4a.branch = develop
p4a.source_dir = 
p4a.bootstrap = sdl2
p4a.local_recipes = 
p4a.hook = 

# Build settings
build_dir = .buildozer
android.release_artifact = aab
android.sign = False
android.deploy = True