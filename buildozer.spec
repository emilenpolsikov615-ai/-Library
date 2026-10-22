[app]

# (str) Title of your application
title = Library

# (str) Package name
package.name = library

# (str) Package domain (needed for android/ios packaging)
package.domain = org.student

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = .venv,.idea,.buildozer,bin,__pycache__

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (list) The Android archs to build for.
# arm64-v8a покрывает все телефоны с ~2017 года и собирается вдвое быстрее,
# чем два архитектурных варианта сразу.
android.archs = arm64-v8a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
