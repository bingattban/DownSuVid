[app]

# (str) Title of your application
title = DownSuVid

# (str) Package name
package.name = downsuviid

# (str) Package domain (needed for android/ios packaging)
package.domain = com.downsuviid

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf,md,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/**,app/**

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, docs, .git, .github, .buildozer

# (list) List of exclusions using pattern matching
source.exclude_patterns = 

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.11.7,hostpython3==3.11.7,kivy==2.2.1,kivymd==1.1.1,yt-dlp,httpx,aiofiles,Pillow,psutil

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
garden_requirements = 

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/splash/splash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icons/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# OSX Specific
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
android.presplash_color = #1A237E

# (string) Presplash animation using Lottie
# android.presplash_lottie = "path/to/lottie/file.json"

# (str) Adaptive icon of the application
# android.adaptive_icon_background.filename = %(source.dir)s/assets/adaptive_background.png
# android.adaptive_icon_foreground.filename = %(source.dir)s/assets/adaptive_foreground.png

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,VIBRATE,POST_NOTIFICATIONS

# (list) features (adds uses-feature -tags to manifest)
#android.features = android.hardware.usb.host

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 26

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support.
android.ndk_api = 26

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = 

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path = 

# (str) ANT directory (if empty, it will be automatically downloaded.)
android.ant_path = 

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only.
android.accept_sdk_agreement = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml attributes to set on the activity element in AndroidManifest.xml
# android.extra_activity_attributes = 

# (list) Java classes to include in the project
# android.add_src = 

# (list) Java jars to include in the project
# android.add_jars = 

# (list) AAR files to include in the project
# android.add_aars = 

# (list) Gradle dependencies to add
# android.gradle_dependencies = 'androidx.core:core:1.10.1','androidx.appcompat:appcompat:1.6.1','com.google.android.material:material:1.9.0'

# (list) Gradle repositories to add
# android.gradle_repositories = 

# (list) add Java compile options
# This can be used to change the target Java version
# android.add_compile_options = "-source" "1.8" "-target" "1.8"

# (str) python-for-android branch to use, defaults to master
p4a.branch = develop

# (str) python-for-android specific fork to use, defaults to None (unspecified)
# p4a.fork = kivy/python-for-android

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
p4a.source_dir = 

# (str) The directory in which python-for-android should look for your own build recipes (if any)
p4a.local_recipes = 

# (str) Filename to the hook for p4a
p4a.hook = 

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
p4a.port = 

# Control passing the --use-setup-py vs --ignore-setup-py to p4a
# "auto" (default) will only pass --use-setup-py if the project has a setup.py
p4a.setup_py = auto

# (str) extra command line arguments to pass when calling python-for-android
# p4a.extra_args = 


#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
ios.kivy_ios_dir = ../kivy-ios

# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# Another platform dependency: ios-deploy
# Uncomment to use a custom checkout
#ios.ios_deploy_dir = ../ios_deploy
# Or specify URL and branch
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# (bool) Whether or not to sign the code
ios.codesign.allowed = false

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, default is under app directory
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#        [app]
#        source.exclude_patterns = .git,3D,test
#
#    This can be translated into:
#
#        [app:source.exclude_patterns]
#        .git
#        3D
#        test
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#        [app@demo]
#        title = My Application (demo)
#
#        [app:source.exclude_patterns@demo]
#        images/hd/**
#
#    Then, invoke the command line with the "demo" profile:
#
#        buildozer --profile demo android debug
