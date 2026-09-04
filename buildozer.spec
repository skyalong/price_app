[app]

title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 🔑 使用 Python 3.11（与系统版本一致）
requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.1.1,plyer,openpyxl

# 🔑 只编译 arm64-v8a
android.arch = arm64-v8a

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21

android.enable_androidx = True
fullscreen = 0
orientation = portrait

log_level = 2
warn_on_root = 0

# 🔑 添加环境变量
android.environment = PYTHONOPTIMIZE=1

# 🔑 使用 develop 分支
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 0