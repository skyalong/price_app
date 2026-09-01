[app]

title = 检校价格系统
package.name = pricequery
package.domain = org.price.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# 必须依赖（指定明确版本，避免兼容性问题）
requirements = python3,kivy==2.3.0,kivymd==1.1.1,plyer,openpyxl

# 安卓权限
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Android SDK/NDK 配置（使用稳定版本）
android.api = 33
android.ndk = 25c
android.minapi = 21
android.sdk = 33

# 打包设置
android.enable_androidx = True
android.gradle_dependencies = 
fullscreen = 0
orientation = portrait

# 日志级别（方便调试）
log_level = 2

# 忽略警告
warn_on_root = 0

[buildozer]

log_level = 2