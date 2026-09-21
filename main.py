

import os
import sys
###################以下####################
import sqlite3
import re
from datetime import datetime
###################以上####################
# 强制使用 Kivy 2.2.1 兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'


from kivy.uix.boxlayout import BoxLayout


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.logger import Logger
from kivy.resources import resource_add_path
#######################以下################
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
#from kivy.uix.label import Label
from kivy.clock import Clock
#from kivy.core.text import LabelBase
#########################以上##############
# 记录启动日志
#LOG_PATH = '/sdcard/simple_app_log.txt'
LOG_PATH = '/storage/emulated/0/simple_app_log.txt'
def write_log(msg):
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(f"{msg}\n")
    except:
        pass

write_log("=" * 50)
write_log("应用启动...")
write_log(f"Python 版本: {sys.version}")

# ==================== 注册中文字体 ====================
FONT_AVAILABLE = False
try:
    resource_add_path(os.path.dirname(os.path.abspath(__file__)))
    LabelBase.register(
        name='ChineseFont',
        fn_regular='NotoSerifCJKsc-Regular.otf'
    )
    FONT_AVAILABLE = True
    write_log("中文字体注册成功")
except Exception as e:
    write_log(f"中文字体注册失败: {e}，将使用默认字体")

# -*- coding: utf-8 -*-
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.label import Label
# from kivy.uix.button import Button

# 在 Python 里构建 KV 字符串之前
if FONT_AVAILABLE:
    FONT_NAME = 'ChineseFont'
else:
    FONT_NAME = 'Roboto'   # Kivy 默认字体

KV = f'''
RootWidget:
    orientation: 'vertical'
    padding: 20
    spacing: 20

    Label:
        text: "Hello, KV，你好!"
        font_name: '{FONT_NAME}'
        font_size: 40
        color: 1, 0, 0, 1

    Button:
        text: "点我"
        font_size: 30
        on_press: root.on_button_click()
'''
# KV = '''
# RootWidget:
#     orientation: 'vertical'
#     padding: 20
#     spacing: 20

#     Label:
#         text: "Hello, KV，你好!"
#         font_name='ChineseFont'
#         font_size: 40
#         color: 1, 0, 0, 1

#     Button:
#         text: "点我"
#         font_size: 30
#         on_press: root.on_button_click()
# '''


class RootWidget(BoxLayout):
    def on_button_click(self):
        print("按钮被点击了！")


class MyApp(App):
    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    MyApp().run()



# KV = '''
# RootWidget:
#     orientation: 'vertical'
#     padding: 20
#     spacing: 20

#     Label:
#         text: "Hello, KV!"
#         font_size: 40
#         color: 1, 0, 0, 1

#     Button:
#         text: "点我"
#         font_size: 30
#         on_press: root.on_button_click()
# '''


# class RootWidget(BoxLayout):
#     def on_button_click(self):
#         print("按钮被点击了！")


# class MyApp(App):
#     def build(self):
#         return Builder.load_string(KV)


# if __name__ == "__main__":
#     MyApp().run()
   #     label = Label(
    #         text="应用运行正常!\n\n如果能看到这个界面,\n说明环境配置正确。",
    #         font_size=30,
    #         font_name='ChineseFont',  # 🔑 使用注册的中文字体
    #         halign='center',
    #         valign='middle'