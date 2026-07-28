[app]

# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------

title = DownSuVid

package.name = downsuvid
package.domain = com.downsuvid

source.dir = .

version = 1.0.0

# ------------------------------------------------------------------
# Source
# ------------------------------------------------------------------

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,txt,ini,xml

source.exclude_exts = pyc,pyo

source.exclude_dirs = \
tests,\
docs,\
.git,\
.github,\
.buildozer,\
venv,\
env,\
__pycache__

source.exclude_patterns = \
.git/*,\
.github/*,\
.buildozer/*

# ------------------------------------------------------------------
# Resources
# ------------------------------------------------------------------

icon.filename = assets/icons/icon.png

presplash.filename = assets/splash/splash.png

# ------------------------------------------------------------------
# Version
# ------------------------------------------------------------------

version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# ------------------------------------------------------------------
# Requirements
# ------------------------------------------------------------------

requirements = python3,kivy,kivymd,yt-dlp,httpx,aiofiles,pillow,psutil

# ------------------------------------------------------------------
# Orientation
# ------------------------------------------------------------------

orientation = portrait

fullscreen = 0

# ------------------------------------------------------------------
# Android SDK
# ------------------------------------------------------------------

android.api = 33

android.minapi = 26

android.sdk = 33

android.ndk = 25b

android.ndk_api = 26

android.accept_sdk_agreement = True

android.private_storage = True

android.allow_backup = True

android.enable_androidx = True

android.archs = arm64-v8a,armeabi-v7a

# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------

android.permissions = \
INTERNET,\
ACCESS_NETWORK_STATE,\
READ_EXTERNAL_STORAGE,\
WRITE_EXTERNAL_STORAGE

# ------------------------------------------------------------------
# Bootstrap
# ------------------------------------------------------------------

p4a.bootstrap = sdl2

# ------------------------------------------------------------------
# Java
# ------------------------------------------------------------------

android.release_artifact = apk

# ------------------------------------------------------------------
# Performance
# ------------------------------------------------------------------

android.copy_libs = 1

# ------------------------------------------------------------------
# Splash
# ------------------------------------------------------------------

presplash.color = #1A237E

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

log_level = 2

# ------------------------------------------------------------------
# Build directory
# ------------------------------------------------------------------

build_dir = .buildozer

# ------------------------------------------------------------------
# Buildozer
# ------------------------------------------------------------------

[buildozer]

log_level = 2

warn_on_root = 1
