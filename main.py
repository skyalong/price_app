# -*- coding: utf-8 -*-
"""
最简测试版本 - 只显示一个界面
用于验证环境是否正常
"""

import os
import sys
###################以下####################
import sqlite3
import re
from datetime import datetime
###################以上####################
# 强制使用 Kivy 2.2.1 兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'

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
#############################以下###############################################
# ==================== KivyMD 导入 ====================
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDTextButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.card import MDCard

# ==================== 导入 openpyxl ====================
try:
    from openpyxl import load_workbook, Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    HAS_OPENPYXL = True
except:
    HAS_OPENPYXL = False

# ==================== Android 权限 ====================
try:
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
    ])
except:
    pass
###############################以上#############################################
###################以下####################
# ==================== 工具函数 ====================
def parse_price(price_str):
    nums = re.findall(r'\d+\.?\d*', str(price_str))
    if nums:
        return float(nums[0])
    return 0.0

def init_db():
    try:
        db_dir = os.path.dirname(DB_NAME)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                model_spec TEXT NOT NULL,
                measure_range TEXT NOT NULL,
                price TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
###################以上####################
###################以下####################

# ==================== KV 界面 ====================
KV = '''
ScreenManager:
    MainScreen:


<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(15)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDLabel:
            text: "标准仪器维检部"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: dp(50)

        MDLabel:
            text: "检校业务价格查询系统"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: dp(40)

        MDRaisedButton:
            text: "单价查询"
            md_bg_color: "#2980b9"
            size_hint: 1, None
            height: dp(55)
            on_press: app.root.current = "client"

        MDRaisedButton:
            text: "批量报价"
            md_bg_color: "#8e44ad"
            size_hint: 1, None
            height: dp(55)
            on_press: app.root.current = "quote"

        MDRaisedButton:
            text: "管理入口"
            md_bg_color: "#c0392b"
            size_hint: 1, None
            height: dp(55)
            on_press: root.show_admin_login()

'''
###################以上####################
###################以下####################
# ==================== 界面类 ====================

class MainScreen(Screen):
    def show_admin_login(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None,
            height=dp(150)
        )
        content.add_widget(MDLabel(text="请输入管理员密码："))
        pwd_input = MDTextField(
            hint_text="密码",
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(pwd_input)

        dialog = MDDialog(
            title="管理员验证",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="取消", on_press=lambda x: dialog.dismiss()),
                MDRaisedButton(
                    text="确定",
                    on_press=lambda x: self.check_password(pwd_input.text, dialog)
                )
            ]
        )
        dialog.open()

    def check_password(self, pwd, dialog):
        if pwd == ADMIN_PASSWORD:
            dialog.dismiss()
            self.manager.current = "admin"
        else:
            Snackbar(text="密码错误！", duration=2).open()


###################以上####################
###################以下####################
# ==================== 主应用 ====================
class PriceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"#主色调为蓝色（按钮、标题高亮色）
        self.theme_cls.theme_style = "Light"#浅色模式；改成`"Dark"`就是暗黑模式
        
        # 设置字体
        self.theme_cls.font_styles.update({
           
            "H4": ["ChineseFont", 34, False, 0.25],
            "H5": ["ChineseFont", 24, False, 0],
            "H6": ["ChineseFont", 20, False, 0.15],
            "Subtitle1": ["ChineseFont", 16, False, 0.15],
            "Body1": ["ChineseFont", 16, False, 0.5],
            "Button": ["ChineseFont", 14, True, 1.25],
            # "H4": ["NotoSansCJK", 34, False, 0.25],
            # "H5": ["NotoSansCJK", 24, False, 0],
            # "H6": ["NotoSansCJK", 20, False, 0.15],
            # "Subtitle1": ["NotoSansCJK", 16, False, 0.15],
            # "Body1": ["NotoSansCJK", 16, False, 0.5],
            # "Button": ["NotoSansCJK", 14, True, 1.25],
        })
        
        #init_db()
        return Builder.load_string(KV)

if __name__ == "__main__":
    PriceApp().run()
###################以上####################