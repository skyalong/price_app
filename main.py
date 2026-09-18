# -*- coding: utf-8 -*-
"""
最简测试版本 - 只显示 main 界面
按钮点击弹窗提示，不跳转
数据库、字体注册暂时屏蔽
"""

import os
import sys

# 强制使用 Kivy 兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar

# ==================== 全局配置 ====================
ADMIN_PASSWORD = "432"

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

        MDLabel:
            text: "标准仪器维检部"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: dp(60)

        MDLabel:
            text: "检校业务价格查询系统"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: dp(50)

        MDRaisedButton:
            text: "单价查询"
            md_bg_color: "#2980b9"
            size_hint: 1, None
            height: dp(55)
            on_press: root.show_msg("单价查询功能待开发")

        MDRaisedButton:
            text: "批量报价"
            md_bg_color: "#8e44ad"
            size_hint: 1, None
            height: dp(55)
            on_press: root.show_msg("批量报价功能待开发")

        MDRaisedButton:
            text: "管理入口"
            md_bg_color: "#c0392b"
            size_hint: 1, None
            height: dp(55)
            on_press: root.show_admin_login()
'''

# ==================== 界面类 ====================
class MainScreen(Screen):
    def show_msg(self, txt):
        dialog = MDDialog(
            text=txt,
            buttons=[MDRaisedButton(text="确定", on_press=lambda x: dialog.dismiss())]
        )
        dialog.open()

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
        content.add_child(pwd_input) if False else content.add_widget(pwd_input)

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
            self.show_msg("密码正确！管理功能待开发")
        else:
            Snackbar(text="密码错误！", duration=2).open()


# ==================== 主应用 ====================
class PriceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)


if __name__ == "__main__":
    PriceApp().run()