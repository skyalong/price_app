# minimal.py
from kivy.app import App
from kivy.uix.label import Label



class MinimalApp(App):
    def build(self):
        return Label(text="Hello World!")


###################################################################################################

##############################################################################################
#if __name__ == "__main__":
    # MinimalApp().run()


class PriceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # 设置字体
        self.theme_cls.font_styles.update({
            "H4": ["NotoSansCJK", 34, False, 0.25],
            "H5": ["NotoSansCJK", 24, False, 0],
            "H6": ["NotoSansCJK", 20, False, 0.15],
            "Subtitle1": ["NotoSansCJK", 16, False, 0.15],
            "Body1": ["NotoSansCJK", 16, False, 0.5],
            "Button": ["NotoSansCJK", 14, True, 1.25],
        })
        
        init_db()
        return Builder.load_string(KV)


if __name__ == "__main__":
    PriceApp().run()