# -*- coding: utf-8 -*-
"""
精简版 - 确保能通过 GitHub Actions 打包
"""

import os
import sys
import traceback

# ==================== 日志 ====================
def write_log(msg):
    """写入日志"""
    try:
        log_path = '/sdcard/app_debug.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{msg}\n")
    except:
        pass

write_log("=" * 50)
write_log("应用启动")

# ==================== Kivy 导入 ====================
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

# 设置窗口大小
Window.size = (400, 700)

# ==================== SQLite ====================
def init_db():
    """初始化数据库"""
    try:
        import sqlite3
        # 使用外部存储
        db_path = '/sdcard/business.db'
        
        conn = sqlite3.connect(db_path)
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
        conn.commit()
        conn.close()
        
        write_log(f"数据库初始化成功: {db_path}")
        return True
    except Exception as e:
        write_log(f"数据库初始化失败: {e}")
        return False

# ==================== 主界面 ====================
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        # 标题
        self.add_widget(Label(
            text="检校价格查询系统",
            font_size=30,
            size_hint_y=0.15
        ))
        
        # 搜索框
        self.search_input = TextInput(
            hint_text="输入检定项目",
            size_hint_y=0.1,
            multiline=False
        )
        self.add_widget(self.search_input)
        
        # 搜索按钮
        search_btn = Button(
            text="查询",
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        search_btn.bind(on_press=self.on_search)
        self.add_widget(search_btn)
        
        # 结果显示
        self.result_label = Label(
            text="请输入关键词查询",
            font_size=18,
            size_hint_y=0.3,
            halign='center'
        )
        self.add_widget(self.result_label)
        
        # 状态标签
        self.status_label = Label(
            text="就绪",
            font_size=14,
            size_hint_y=0.1
        )
        self.add_widget(self.status_label)
        
        # 初始化数据库
        if init_db():
            self.status_label.text = "数据库已初始化"

    def on_search(self, instance):
        """搜索"""
        keyword = self.search_input.text.strip()
        if not keyword:
            self.result_label.text = "请输入关键词"
            return
        
        self.status_label.text = f"搜索: {keyword}"
        self.result_label.text = f"搜索 '{keyword}' 的结果"
        
        # 实际查询数据库
        try:
            import sqlite3
            conn = sqlite3.connect('/sdcard/business.db')
            c = conn.cursor()
            c.execute(
                "SELECT project_name, model_spec, measure_range, price FROM capabilities WHERE project_name LIKE ?",
                (f"%{keyword}%",)
            )
            rows = c.fetchall()
            conn.close()
            
            if rows:
                text = "\n".join([f"{r[0]}: {r[3]}" for r in rows[:5]])
                self.result_label.text = f"找到 {len(rows)} 条结果\n{text}"
            else:
                self.result_label.text = "暂不开展此项业务"
                
        except Exception as e:
            self.result_label.text = f"查询错误: {e}"
            write_log(f"查询错误: {e}")

# ==================== 应用 ====================
class PriceApp(App):
    def build(self):
        write_log("应用构建开始")
        return MainScreen()
    
    def on_start(self):
        write_log("应用启动完成")
    
    def on_stop(self):
        write_log("应用停止")

if __name__ == "__main__":
    write_log("运行应用...")
    try:
        PriceApp().run()
    except Exception as e:
        write_log(f"应用运行失败: {traceback.format_exc()}")
        raise