


[app]
title = 检校业务单价查询
package.name = simpletest
package.domain = org.test

source.include_exts = py,png,jpg,kv,atlas,otf,ttf,pyc,so,json,txt
source.include_patterns = NotoSerifCJKsc-Regular.otf

requirements = python3,kivy==2.2.1,kivymd==1.1.1,android,pyjnius

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# 关键：禁用图标复制（部分 p4a 版本支持）
# android.copy_icons = 0