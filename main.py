

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
try:
    # 添加当前目录到资源路径
    resource_add_path(os.path.dirname(os.path.abspath(__file__)))
    
    # 注册中文字体
    LabelBase.register(
        name='ChineseFont',
        fn_regular= 'NotoSerifCJKsc-Regular.otf'#'NotoSansSC-Regular.otf'
    )
    write_log("中文字体注册成功")
except Exception as e:
    write_log(f"中文字体注册失败: {e}")

# -*- coding: utf-8 -*-
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.label import Label
# from kivy.uix.button import Button


KV = '''
RootWidget:
    orientation: 'vertical'
    padding: 20
    spacing: 20

    Label:
        text: "标准仪器维检部"
        font_style: "H4"
        halign: "center"
        size_hint_y: None
        height: dp(50)

    Button:
        text: "点我"
        font_size: 30
        on_press: root.on_button_click()
'''


class RootWidget(BoxLayout):
    def on_button_click(self):
        print("按钮被点击了！")


class MyApp(App):
    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    MyApp().run()

        # text: "标准仪器维检部"
        # font_size: 40
        # font_name='ChineseFont'
        # color: 1, 0, 0, 1