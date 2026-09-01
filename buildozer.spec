[app]
title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd==1.1.1,plyer,openpyxl

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21
android.build_tools = 33.0.0

android.enable_androidx = True
fullscreen = 0
orientation = portrait

log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2