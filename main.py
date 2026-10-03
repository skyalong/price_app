# -*- coding: utf-8 -*-
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText


class MyApp(MDApp):
    def build(self):
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        layout.add_widget(MDLabel(
            text="Hello KivyMD",
            halign="center"
        ))
        layout.add_widget(MDButton(
            MDButtonText(text="点我"),
            style="elevated",          # 对应旧的 MDRaisedButton
            pos_hint={"center_x": 0.5},
            on_release=self.on_button_click,
        ))
        return layout

    def on_button_click(self, instance):
        print("按钮被点击了")


if __name__ == "__main__":
    MyApp().run()