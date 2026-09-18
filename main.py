# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(20)

    MDLabel:
        text: "Hello, KivyMD!"
        halign: "center"
        font_style: "H4"

    MDRaisedButton:
        text: "点我"
        pos_hint: {"center_x": 0.5}
        on_press: root.on_button_click()
'''


class RootWidget(MDBoxLayout):
    def on_button_click(self):
        print("KivyMD 按钮被点击了！")


class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    MyApp().run()