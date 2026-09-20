# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


KV = '''
RootWidget:
    orientation: 'vertical'
    padding: 20
    spacing: 20

    Label:
        text: "Hello, KV!"
        font_size: 40
        color: 1, 0, 0, 1

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