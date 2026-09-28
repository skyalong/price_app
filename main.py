# -*- coding: utf-8 -*-
import os
import sys

# 强制使用兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog


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


# ==================== KV 界面 ====================
KV = f'''
MDScreenManager:
    SingleQueryScreen:

<SingleQueryScreen>:
    name: "single_query"

    MDBoxLayout:
        orientation: "vertical"

        # ========== 顶部工具栏 ==========
        MDBoxLayout:
            size_hint_y: None
            height: dp(56)
            md_bg_color: "#2c3e50"
            padding: dp(4), dp(4)
            spacing: dp(4)

            MDRaisedButton:
                text: "管理入口"
                font_name: '{FONT_NAME}'
                md_bg_color: "#c0392b"
                size_hint_x: 0.33
                on_press: root.show_msg("管理入口功能待开发")

            MDRaisedButton:
                text: "单价查询"
                font_name: '{FONT_NAME}'
                md_bg_color: "#2980b9"
                size_hint_x: 0.34
                on_press: root.show_msg("当前已是单价查询页")

            MDRaisedButton:
                text: "批量报价"
                font_name: '{FONT_NAME}'
                md_bg_color: "#8e44ad"
                size_hint_x: 0.33
                on_press: root.show_msg("批量报价功能待开发")

        # ========== 内容区 ==========
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(15)
            spacing: dp(15)

            MDLabel:
                text: "检校业务单价查询"
                font_name: '{FONT_NAME}'
                halign: "center"
                font_style: "H5"
                size_hint_y: None
                height: dp(50)

            MDBoxLayout:
                size_hint_y: None
                height: dp(60)
                spacing: dp(10)

                MDLabel:
                    text: "检定项目："
                    font_name: '{FONT_NAME}'
                    size_hint_x: 0.25
                    halign: "right"
                    valign: "middle"

                MDTextField:
                    id: search_input
                    font_name: '{FONT_NAME}'
                    hint_text: "请输入关键词"
                    size_hint_x: 0.5
                    mode: "rectangle"

                MDRaisedButton:
                    text: "查询"
                    font_name: '{FONT_NAME}'
                    md_bg_color: "#2980b9"
                    size_hint_x: 0.25
                    on_press: root.do_search()
'''


# ==================== 界面类 ====================
class SingleQueryScreen(MDScreen):
    def do_search(self):
        key = self.ids.search_input.text.strip()
        if key:
            self.show_msg(f"搜索：{key}")
        else:
            self.show_msg("请输入搜索关键词")

    def show_msg(self, txt):
        dialog = MDDialog(
            text=txt,
            buttons=[MDRaisedButton(
                text="确定",
                font_name=FONT_NAME,
                on_press=lambda x: dialog.dismiss()
            )]
        )
        dialog.open()


# ==================== 主应用 ====================
class PriceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        if FONT_AVAILABLE:
            self.theme_cls.font_styles.update({
                "H4": ["ChineseFont", 34, False, 0.25],
                "H5": ["ChineseFont", 24, False, 0],
                "H6": ["ChineseFont", 20, False, 0.15],
                "Subtitle1": ["ChineseFont", 16, False, 0.15],
                "Body1": ["ChineseFont", 16, False, 0.5],
                "Button": ["ChineseFont", 14, True, 1.25],
            })

        return Builder.load_string(KV)


if __name__ == "__main__":
    PriceApp().run()