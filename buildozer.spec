[app]

title = DownSuVid
package.name = downsuviid
package.domain = com.downsuviid

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
source.exclude_dirs = tests,docs,.git,.github,.buildozer,venv,__pycache__

version = 1.0.0

requirements = python3,kivy,yt-dlp

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.private_storage = True
android.accept_sdk_agreement = True
android.entrypoint = org.kivy.android.PythonActivity

p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
