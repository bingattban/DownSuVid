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
source.exclude_dirs = tests,docs,.git,.github,.buildozer,venv,__pycache__

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,yt-dlp

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Presplash background color
android.presplash_color = #1A237E

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 26

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 26

# (bool) Use --private data storage
android.private_storage = True

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_agreement = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) python-for-android branch to use
p4a.branch = develop

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
