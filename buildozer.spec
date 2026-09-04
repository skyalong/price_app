[app]

title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 🔑 关键：添加 font 支持
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.1.1,plyer,openpyxl

# 🔑 关键：只编译 arm64-v8a
android.arch = arm64-v8a

# 🔑 关键：添加系统字体支持
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21

android.enable_androidx = True
fullscreen = 0
orientation = portrait

# 🔑 关键：添加字体文件
android.add_src = 
android.extra_android_dependencies = 

# 🔑 关键：Kivy 设置
log_level = 2
warn_on_root = 0