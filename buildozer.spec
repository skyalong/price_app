[app]

title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 🔑 使用预编译的 Python（关键！）
requirements = python3,kivy==2.2.1,kivymd==1.1.1,plyer,openpyxl

# 🔑 不指定 Python 版本，让 buildozer 使用预编译版本
# 不要写 python3==3.11.9

# 🔑 只编译 arm64-v8a
android.archs = arm64-v8a

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

# 🔑 使用 develop 分支获取最新优化
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 0