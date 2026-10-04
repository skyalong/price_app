[app]
title = Simple Test
package.name = simpletest
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,otf,ttf,ttc,pyc,so,json,txt

version = 1.0.0

requirements = python3==3.9.1,kivy==2.3.1,kivymd==2.0.0,android,pyjnius

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21
android.arch = arm64-v8a
android.copy_icons = 0
android.enable_androidx = True
fullscreen = 0
orientation = portrait

log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2

