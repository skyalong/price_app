# -*- coding: utf-8 -*-
"""
检校业务价格查询系统 - Android 精简版
先确保能运行，再扩展功能
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
import sqlite3
import os
import sys
import traceback

# ==================== 错误日志 ====================
def log_error(msg):
    """记录错误到文件"""
    try:
        # 尝试写入应用私有目录
        from android.storage import app_storage_path
        log_path = os.path.join(app_storage_path(), 'error_log.txt')
    except:
        log_path = '/sdcard/error_log.txt'
    
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{msg}\n")
            f.write("=" * 50 + "\n")
    except:
        pass

# ==================== 数据库路径 ====================
def get_db_path():
    """获取数据库路径 - 最安全的方式"""
    try:
        from android.storage import app_storage_path
        path = os.path.join(app_storage_path(), 'business.db')
        log_error(f"使用 app_storage_path: {path}")
        return path
    except Exception as e:
        log_error(f"app_storage_path 失败: {e}")
    
    # 备选方案1：内部存储
    try:
        path = '/data/data/org.price.pricequery/files/business.db'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        log_error(f"使用固定路径: {path}")
        return path
    except:
        pass
    
    # 备选方案2：外部存储
    try:
        path = '/sdcard/Android/data/org.price.pricequery/files/business.db'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        log_error(f"使用外部存储路径: {path}")
        return path
    except:
        pass
    
    # 最后备选
    log_error("使用当前目录")
    return 'business.db'

DB_NAME = get_db_path()
ADMIN_PASSWORD = "432"

# ==================== 初始化数据库 ====================
def init_db():
    """初始化数据库"""
    try:
        log_error(f"初始化数据库: {DB_NAME}")
        
        # 确保目录存在
        db_dir = os.path.dirname(DB_NAME)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            log_error(f"创建目录: {db_dir}")
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                model_spec TEXT NOT NULL,
                measure_range TEXT NOT NULL,
                price TEXT NOT NULL
            )
        ''')
        # 插入测试数据
        c.execute("SELECT COUNT(*) FROM capabilities")
        count = c.fetchone()[0]
        if count == 0:
            log_error("插入测试数据")
            c.execute("INSERT INTO capabilities (project_name, model_spec, measure_range, price) VALUES (?,?,?,?)",
                      ("电子天平", "FA2004N", "0-200g", "800元"))
            c.execute("INSERT INTO capabilities (project_name, model_spec, measure_range, price) VALUES (?,?,?,?)",
                      ("酸度计", "PHS-3C", "0-14pH", "600元"))
        conn.commit()
        conn.close()
        log_error("数据库初始化成功")
        return True
    except Exception as e:
        log_error(f"数据库初始化失败: {traceback.format_exc()}")
        return False

# ==================== KV 界面 ====================
KV = '''
ScreenManager:
    MainScreen:
    TestScreen:

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(20)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDLabel:
            text: "检校价格查询系统"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: dp(60)

        MDLabel:
            text: "v1.0 - 测试版"
            halign: "center"
            size_hint_y: None
            height: dp(30)

        MDRaisedButton:
            text: "进入测试页面"
            md_bg_color: "#2980b9"
            size_hint: 1, None
            height: dp(60)
            on_press: app.root.current = "test"

        MDRaisedButton:
            text: "管理入口"
            md_bg_color: "#c0392b"
            size_hint: 1, None
            height: dp(60)
            on_press: root.show_admin_login()

<TestScreen>:
    name: "test"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(10)

        MDTopAppBar:
            title: "测试页面"
            left_action_items: [["arrow-left", lambda x: setattr(app.root, "current", "main")]]
            elevation: 4

        MDLabel:
            id: info_label
            text: "数据库状态: 加载中..."
            halign: "center"
            size_hint_y: None
            height: dp(50)

        MDScrollView:
            MDBoxLayout:
                id: data_box
                orientation: "vertical"
                size_hint: 1, None
                height: self.minimum_height
                spacing: dp(5)

        MDRaisedButton:
            text: "刷新数据"
            size_hint: 1, None
            height: dp(50)
            on_press: root.load_data()
'''

# ==================== 页面类 ====================

class MainScreen(Screen):
    def show_admin_login(self):
        """显示管理员登录"""
        try:
            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(10),
                size_hint_y=None,
                height=dp(150)
            )
            content.add_widget(MDLabel(text="请输入管理员密码："))
            pwd_input = MDTextField(
                hint_text="密码",
                password=True,
                size_hint_y=None,
                height=dp(50)
            )
            content.add_widget(pwd_input)

            dialog = MDDialog(
                title="管理员验证",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="取消", on_press=lambda x: dialog.dismiss()),
                    MDRaisedButton(
                        text="确定",
                        on_press=lambda x: self.check_password(pwd_input.text, dialog)
                    )
                ]
            )
            dialog.open()
        except Exception as e:
            log_error(f"显示登录对话框失败: {e}")
            Snackbar(text=f"错误: {str(e)}", duration=3).open()

    def check_password(self, pwd, dialog):
        if pwd == ADMIN_PASSWORD:
            dialog.dismiss()
            Snackbar(text="登录成功！", duration=2).open()
            self.manager.current = "test"
        else:
            Snackbar(text="密码错误！", duration=2).open()


class TestScreen(Screen):
    def on_enter(self):
        """进入页面时加载数据"""
        self.load_data()

    def load_data(self):
        """加载并显示数据库数据"""
        try:
            self.ids.info_label.text = "正在加载数据..."
            self.ids.data_box.clear_widgets()

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, project_name, model_spec, measure_range, price FROM capabilities")
            rows = c.fetchall()
            conn.close()

            if not rows:
                self.ids.info_label.text = "暂无数据"
                label = MDLabel(text="数据库为空，请添加数据", halign="center")
                self.ids.data_box.add_widget(label)
                return

            self.ids.info_label.text = f"共有 {len(rows)} 条数据"

            # 显示数据
            for row in rows:
                card = MDBoxLayout(
                    orientation="vertical",
                    padding=dp(10),
                    size_hint_y=None,
                    height=dp(80)
                )
                card.add_widget(MDLabel(text=f"项目: {row[1]}", font_style="Subtitle1"))
                card.add_widget(MDLabel(text=f"型号: {row[2]} | 范围: {row[3]} | 价格: {row[4]}", theme_text_color="Secondary"))
                self.ids.data_box.add_widget(card)

        except Exception as e:
            log_error(f"load_data 错误: {traceback.format_exc()}")
            self.ids.info_label.text = f"加载失败: {str(e)}"
            Snackbar(text=f"加载失败: {str(e)}", duration=3).open()


# ==================== 主应用 ====================
class PriceApp(MDApp):
    def build(self):
        """构建应用"""
        try:
            log_error("=" * 50)
            log_error("应用启动...")
            
            # 设置主题
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.theme_style = "Light"
            
            # 初始化数据库
            if not init_db():
                log_error("数据库初始化失败，应用可能无法正常工作")
            
            # 加载界面
            return Builder.load_string(KV)
            
        except Exception as e:
            log_error(f"build 失败: {traceback.format_exc()}")
            # 返回一个简单的界面，避免完全崩溃
            return Builder.load_string('''
ScreenManager:
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(50)
        MDLabel:
            text: "应用启动失败"
            halign: "center"
        MDLabel:
            text: "请查看 error_log.txt"
            halign: "center"
''')


if __name__ == "__main__":
    PriceApp().run()