# -*- coding: utf-8 -*-
"""
最简测试版本 - 只显示一个界面
用于验证环境是否正常
"""

import os
import sys

# 强制使用 Kivy 2.2.1 兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.logger import Logger
from kivy.resources import resource_add_path

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


class SimpleApp(App):
    def build(self):
        write_log("build() 开始执行")
        
        try:
            layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
            
            label = Label(
                text="应用运行正常!\n\n如果能看到这个界面,\n说明环境配置正确。",
                font_size=30,
                font_name='ChineseFont',  # 🔑 使用注册的中文字体
                halign='center',
                valign='middle'
            )
            layout.add_widget(label)
            
            btn = Button(
                text="点击测试",
                font_size=20,
                font_name='ChineseFont',  # 🔑 按钮也使用中文字体
                size_hint=(1, 0.2)
            )
            btn.bind(on_press=self.on_button_click)
            layout.add_widget(btn)

            ############################
            btn1 = Button(
                text="管理入口",
                font_size=20,
                font_name='ChineseFont',  # 🔑 按钮也使用中文字体
                size_hint=(1, 0.2)
            )
            btn1.bind(on_press=self.on_button_click)
            layout.add_widget(btn1)

            btn2 = Button(
                text="单价查询",
                font_size=20,
                font_name='ChineseFont',  # 🔑 按钮也使用中文字体
                size_hint=(1, 0.2)
            )
            btn2.bind(on_press=self.on_button_click)
            layout.add_widget(btn2)
            btn3 = Button(
                text="批量报价",
                font_size=20,
                font_name='ChineseFont',  # 🔑 按钮也使用中文字体
                size_hint=(1, 0.2)
            )
            btn3.bind(on_press=self.on_button_click)
            layout.add_widget(btn3)
            ############################
            write_log("build() 执行成功")
            return layout
            
        except Exception as e:
            write_log(f"build() 错误: {e}")
            raise

    def on_button_click(self, instance):
        write_log("按钮被点击")
        instance.text = "点击成功!"


if __name__ == "__main__":
    write_log("开始运行 SimpleApp")
    try:
        SimpleApp().run()
    except Exception as e:
        write_log(f"运行失败: {e}")
        raise