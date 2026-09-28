# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import re
from datetime import datetime

# 强制使用 Kivy 2.2.1 兼容模式
os.environ['KIVY_GL_BACKEND'] = 'gl'#os.environ['KIVY_ENCODING'] = 'utf-8'

from kivy.app import App
from kivy.logger import Logger
from kivy.resources import resource_add_path

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.text import LabelBase

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