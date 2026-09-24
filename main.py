# -*- coding: utf-8 -*-
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton


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
        layout.add_widget(MDRaisedButton(
            text="点我"
        ))
        return layout


if __name__ == "__main__":
    MyApp().run()