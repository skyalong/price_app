# -*- coding: utf-8 -*-
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


# ========== 定义4个页面 ==========
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.add_widget(MDLabel(text="标准仪器维检部【首页】", font_style="H4", halign="center"))
        layout.add_widget(MDRaisedButton(text="进入客户查询页", on_press=self.goto_client))
        layout.add_widget(MDRaisedButton(text="进入管理员页面", on_press=self.goto_admin))
        layout.add_widget(MDRaisedButton(text="进入报价页面", on_press=self.goto_quote))
        self.add_widget(layout)

    def goto_client(self, *args):
        self.manager.current = "client"
    def goto_admin(self, *args):
        self.manager.current = "admin"
    def goto_quote(self, *args):
        self.manager.current = "quote"


class ClientScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.add_widget(MDLabel(text="客户查询页面", font_style="H4", halign="center"))
        layout.add_widget(MDRaisedButton(text="返回首页", on_press=self.goto_main))
        self.add_widget(layout)
    def goto_main(self, *args):
        self.manager.current = "main"


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.add_widget(MDLabel(text="管理员后台页面", font_style="H4", halign="center"))
        layout.add_widget(MDRaisedButton(text="返回首页", on_press=self.goto_main))
        self.add_widget(layout)
    def goto_main(self, *args):
        self.manager.current = "main"


class QuoteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.add_widget(MDLabel(text="报价单页面", font_style="H4", halign="center"))
        layout.add_widget(MDRaisedButton(text="返回首页", on_press=self.goto_main))
        self.add_widget(layout)
    def goto_main(self, *args):
        self.manager.current = "main"


# ========== 外层容器：PriceApp 继承BoxLayout（就是你刚才那段代码） ==========
class PriceApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        # ScreenManager
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(ClientScreen(name="client"))
        self.sm.add_widget(AdminScreen(name="admin"))
        self.sm.add_widget(QuoteScreen(name="quote"))
        self.sm.current = "main"
        self.add_widget(self.sm)


# ========== MDApp 程序入口 ==========
class MyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return PriceApp()


if __name__ == "__main__":
    MyApp().run()
