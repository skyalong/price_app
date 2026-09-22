[app]
title = 检校价格查询系统
package.name = pricequery
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,otf,ttf,ttc,db,xlsx

version = 1.0

requirements = python3,kivy==2.3.0,sqlite3,openpyxl,pyjnius

# Android 权限
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# 安卓 SDK/NDK 版本
android.api = 33
android.ndk = 25b
android.minapi = 21

# 架构
android.archs = arm64-v8a, armeabi-v7a

# 全屏
android.fullscreen = 0

# 图标（自行替换）
# icon.filename = icon.png

# 引导画面
# presplash.filename = presplash.png

# 构建目录
build_dir = .buildozer

# 日志
log_level = 2
