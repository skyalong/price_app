# -*- coding: utf-8 -*-
import os
import sys

# 强制使用兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar


# ==================== 日志 ====================
def get_log_path():
    try:
        from kivy.utils import platform
        if platform == 'android':
            return '/storage/emulated/0/simple_app_log.txt'
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simple_app_log.txt')
    except:
        return 'simple_app_log.txt'

LOG_PATH = get_log_path()

def write_log(msg):
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
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

if FONT_AVAILABLE:
    FONT_NAME = 'ChineseFont'
else:
    FONT_NAME = 'Roboto'


# ==================== 全局配置 ====================
ADMIN_PASSWORD = "432"


# ==================== KV 界面 ====================
KV = f'''
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
            font_name: '{FONT_NAME}'
            halign: "center"
            font_style: "H4"
            size_hint_y: None
            height: dp(60)

        MDLabel:
            text: "检校业务价格查询系统"
            font_name: '{FONT_NAME}'
            halign: "center"
            font_style: "H5"
            size_hint_y: None
            height: dp(50)

        MDRaisedButton:
            text: "单价查询"
            font_name: '{FONT_NAME}'
            md_bg_color: "#2980b9"
            size_hint: 1, None
            height: dp(55)
            on_press: root.show_msg("单价查询功能待开发")

        MDRaisedButton:
            text: "批量报价"
            font_name: '{FONT_NAME}'
            md_bg_color: "#8e44ad"
            size_hint: 1, None
            height: dp(55)
            on_press: root.show_msg("批量报价功能待开发")

        MDRaisedButton:
            text: "管理入口"
            font_name: '{FONT_NAME}'
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
        content.add_widget(MDLabel(text="请输入管理员密码：", font_name=FONT_NAME))
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
            self.show_msg("密码正确！管理功能待开发")
        else:
            Snackbar(text="密码错误！", duration=2).open()


# ==================== 主应用 ====================
class PriceApp(MDApp):
    def build(self):
        # self.theme_cls.primary_palette = "Blue"
        # self.theme_cls.theme_style = "Light"

        # # 关键：把 KivyMD 的字体样式也替换成中文字体
        # if FONT_AVAILABLE:
        #     self.theme_cls.font_styles.update({
        #         "H4": ["ChineseFont", 34, False, 0.25],
        #         "H5": ["ChineseFont", 24, False, 0],
        #         "H6": ["ChineseFont", 20, False, 0.15],
        #         "Subtitle1": ["ChineseFont", 16, False, 0.15],
        #         "Body1": ["ChineseFont", 16, False, 0.5],
        #         "Button": ["ChineseFont", 14, True, 1.25],
        #     })

        return Builder.load_string(KV)


if __name__ == "__main__":
    PriceApp().run()