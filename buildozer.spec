[app]
title = 巡检记录
package.name = xunjian
package.domain = org.xunjian

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,otf,ttf,ttc,pyc,so,json,txt

version = 1.0.0
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,android,pyjnius

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25c
android.minapi = 21
android.archs = arm64-v8a
android.copy_icons = 0
android.enable_androidx = True
fullscreen = 0
orientation = portrait

log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2