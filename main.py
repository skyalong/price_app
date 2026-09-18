# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivy.app import App

# ==================== KV 字符串 ====================
KV = '''
BoxLayout:
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


# ==================== 根控件类 ====================
class RootWidget(BoxLayout):
    def on_button_click(self):
        print("按钮被点击了！")


# ==================== 主应用 ====================
class MyApp(App):
    def build(self):
        # 方式一：直接在 build 里加载 KV 字符串
        #return Builder.load_string(KV)
        return 

if __name__ == "__main__":
    MyApp().run()