[app]
title = Simple Test
package.name = simpletest
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,otf,ttf,ttc

version = 1.0.0

requirements = python3==3.11.9,kivy

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21
android.arch = arm64-v8a

android.enable_androidx = True
fullscreen = 0
orientation = portrait

log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2