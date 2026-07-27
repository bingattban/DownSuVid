[app]

# (str) Title of your application
title = DownSuVid

# (str) Package name
package.name = downsuviid

# (str) Package domain
package.domain = com.downsuviid

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (list) List of directory to exclude
source.exclude_dirs = tests,docs,.git,.github,.buildozer,venv,app

# (str) Application versioning
version = 1.0.0

# (list) Application requirements - minimal
requirements = python3,kivy

# (str) Icon of the application
#icon.filename = %(source.dir)s/icon.png

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/presplash.png

# (str) Supported orientation
orientation = portrait

# Android specific
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.sdk = 33
android.ndk = 25b
android.ndk_api = 26
android.private_storage = True
android.accept_sdk_agreement = True

# p4a settings
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
