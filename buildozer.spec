[app]

title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 🔑 使用 Python 3.9（稳定且编译快）
requirements = python3==3.9,kivy==2.1.0,kivymd==1.1.1,plyer,openpyxl

# 🔑 只编译 arm64-v8a
android.archs = arm64-v8a

# 🔑 权限
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# 🔑 SDK 配置
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21

android.enable_androidx = True
fullscreen = 0
orientation = portrait

log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2
warn_on_root = 0