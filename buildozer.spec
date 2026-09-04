[app]

title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 🔑 关键：使用 Python 3.9.10
requirements = python3==3.9.10,kivy==2.2.1,kivymd==1.1.1,plyer,openpyxl

# 🔑 只编译 arm64-v8a（现代手机都支持）
android.arch = arm64-v8a

# 🔑 权限
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# 🔑 SDK 版本
android.api = 33
android.ndk = 25c
android.sdk = 33
android.minapi = 21

android.enable_androidx = True

# 🔑 减少 APK 大小
android.gradle_dependencies = 
android.add_src = 
android.add_assets = 

# 🔑 应用设置
fullscreen = 0
orientation = portrait

# 🔑 日志
log_level = 2
warn_on_root = 0

# 🔑 跳过测试编译
android.environment = PYTHONOPTIMIZE=1

# 🔑 使用 develop 分支
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 0