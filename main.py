# -*- coding: utf-8 -*-
"""
标准仪器维检部检校业务价格查询系统 - Android版
修复闪退问题
"""

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDTextButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
import sqlite3
import re
import os
import sys
import traceback

# ==================== 错误日志记录 ====================
def log_error(msg):
    """记录错误到文件，便于调试"""
    try:
        from android.storage import app_storage_path
        log_path = os.path.join(app_storage_path(), 'error_log.txt')
    except:
        log_path = 'error_log.txt'
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{msg}\n")
        f.write("=" * 50 + "\n")

# ==================== Android 权限 ====================
def request_permissions_safe():
    """安全地请求权限"""
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
        return True
    except Exception as e:
        log_error(f"权限申请失败: {e}")
        return False

# ==================== 路径配置 ====================
def get_db_path():
    """获取应用私有目录下的数据库路径 - 修复版本"""
    try:
        from android.storage import app_storage_path
        # 确保目录存在
        storage_path = app_storage_path()
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
        path = os.path.join(storage_path, 'business.db')
        log_error(f"数据库路径: {path}")
        return path
    except Exception as e:
        log_error(f"获取存储路径失败: {e}")
        # 使用当前目录作为备选
        return os.path.join(os.getcwd(), 'business.db')

DB_NAME = get_db_path()
ADMIN_PASSWORD = "432"
EXCEL_HEADERS = ["检定项目", "型号规格", "测量范围", "价格"]

# ==================== 解析函数 ====================
def parse_price(price_str):
    """从价格字符串中提取数字"""
    try:
        nums = re.findall(r'\d+\.?\d*', str(price_str))
        if nums:
            return float(nums[0])
    except:
        pass
    return 0.0

# ==================== 数据库初始化 ====================
def init_db():
    """初始化数据库 - 带错误处理"""
    try:
        log_error(f"开始初始化数据库: {DB_NAME}")
        
        # 确保目录存在
        db_dir = os.path.dirname(DB_NAME)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            log_error(f"创建数据库目录: {db_dir}")

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                model_spec TEXT NOT NULL,
                measure_range TEXT NOT NULL,
                price TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        log_error("数据库初始化成功")
        return True
    except Exception as e:
        log_error(f"数据库初始化失败: {traceback.format_exc()}")
        return False

# ==================== KV 字符串 ====================
KV = '''
ScreenManager:
    MainScreen:
    AdminScreen:
    QuoteScreen:
    ClientScreen:

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(20)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDLabel:
            text: "标准仪器维检部"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: dp(50)

        MDLabel:
            text: "检校业务价格查询系统"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: dp(40)

        MDRaisedButton:
            text: "单价查询"
            md_bg_color: "#2980b9"
            size_hint: 1, None
            height: dp(60)
            on_press: app.root.current = "client"

        MDRaisedButton:
            text: "批量报价"
            md_bg_color: "#8e44ad"
            size_hint: 1, None
            height: dp(60)
            on_press: app.root.current = "quote"

        MDRaisedButton:
            text: "管理入口"
            md_bg_color: "#c0392b"
            size_hint: 1, None
            height: dp(60)
            on_press: root.show_admin_login()

<ClientScreen>:
    name: "client"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(10)

        MDTopAppBar:
            title: "单价查询"
            left_action_items: [["arrow-left", lambda x: setattr(app.root, "current", "main")]]
            elevation: 4

        MDBoxLayout:
            size_hint: 1, None
            height: dp(50)
            spacing: dp(10)
            padding: dp(5)

            MDTextField:
                id: search_key
                hint_text: "输入检定项目搜索"
                size_hint: 0.7, 1
                on_text_validate: root.search_data()

            MDRaisedButton:
                text: "查询"
                size_hint: 0.3, 1
                on_press: root.search_data()

        MDLabel:
            id: tip_text
            text: ""
            halign: "center"
            theme_text_color: "Error"
            size_hint_y: None
            height: dp(30)

        MDScrollView:
            size_hint: 1, 1
            MDBoxLayout:
                id: table_box
                size_hint: 1, None
                height: dp(600)
                orientation: "vertical"

<AdminScreen>:
    name: "admin"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)

        MDTopAppBar:
            title: "管理后台"
            left_action_items: [["arrow-left", lambda x: setattr(app.root, "current", "main")]]
            elevation: 4

        MDScrollView:
            size_hint: 1, 1
            do_scroll_x: False
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(8)
                size_hint: 1, None
                height: self.minimum_height

                MDTextField:
                    id: e1
                    hint_text: "检定项目"
                    size_hint: 1, None
                    height: dp(45)
                MDTextField:
                    id: e2
                    hint_text: "型号规格"
                    size_hint: 1, None
                    height: dp(45)
                MDTextField:
                    id: e3
                    hint_text: "测量范围"
                    size_hint: 1, None
                    height: dp(45)
                MDTextField:
                    id: e4
                    hint_text: "价格"
                    size_hint: 1, None
                    height: dp(45)

                MDLabel:
                    id: edit_tip
                    text: ""
                    theme_text_color: "Error"
                    size_hint_y: None
                    height: dp(30)

                MDBoxLayout:
                    spacing: dp(5)
                    size_hint: 1, None
                    height: dp(45)

                    MDRaisedButton:
                        text: "保存"
                        md_bg_color: "#27ae60"
                        on_press: root.save_data()
                    MDRaisedButton:
                        text: "修改"
                        md_bg_color: "#f39c12"
                        on_press: root.edit_data()
                    MDRaisedButton:
                        text: "删除"
                        md_bg_color: "#e74c3c"
                        on_press: root.del_data()

                MDBoxLayout:
                    spacing: dp(5)
                    size_hint: 1, None
                    height: dp(45)

                    MDRaisedButton:
                        text: "刷新列表"
                        md_bg_color: "#3498db"
                        on_press: root.load_list()
                    MDRaisedButton:
                        text: "导入Excel"
                        md_bg_color: "#9b59b6"
                        on_press: root.import_from_excel()

                MDLabel:
                    text: "数据列表（点击选中）"
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: dp(30)

                MDScrollView:
                    size_hint: 1, None
                    height: dp(350)
                    MDBoxLayout:
                        id: admin_table_box
                        size_hint: 1, None
                        height: dp(600)
                        orientation: "vertical"

<QuoteScreen>:
    name: "quote"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)

        MDTopAppBar:
            title: "批量报价"
            left_action_items: [["arrow-left", lambda x: setattr(app.root, "current", "main")]]
            elevation: 4

        MDBoxLayout:
            size_hint: 1, None
            height: dp(45)
            spacing: dp(8)

            MDTextField:
                id: q_search
                hint_text: "搜索检定项目"
                size_hint: 0.7, 1
                on_text_validate: root.q_search()

            MDRaisedButton:
                text: "搜索"
                size_hint: 0.3, 1
                on_press: root.q_search()

        MDLabel:
            text: "查询结果"
            font_style: "Subtitle1"
            size_hint_y: None
            height: dp(25)

        MDScrollView:
            size_hint: 1, 0.3
            MDBoxLayout:
                id: q_table_box
                size_hint: 1, None
                height: dp(250)
                orientation: "vertical"

        MDBoxLayout:
            size_hint: 1, None
            height: dp(45)
            spacing: dp(8)

            MDTextField:
                id: qty_input
                hint_text: "数量"
                text: "1"
                size_hint: 0.35, 1
                input_filter: "float"

            MDRaisedButton:
                text: "加入报价单"
                md_bg_color: "#27ae60"
                size_hint: 0.65, 1
                on_press: root.add_cart()

        MDLabel:
            text: "报价单列表（点击选中删除）"
            font_style: "Subtitle1"
            size_hint_y: None
            height: dp(25)

        MDScrollView:
            size_hint: 1, 0.3
            MDBoxLayout:
                id: cart_box
                size_hint: 1, None
                height: dp(250)
                orientation: "vertical"

        MDLabel:
            id: total_text
            text: "总金额：0.00 元"
            font_style: "H6"
            theme_text_color: "Error"
            halign: "center"
            size_hint_y: None
            height: dp(40)

        MDBoxLayout:
            spacing: dp(5)
            size_hint: 1, None
            height: dp(45)

            MDRaisedButton:
                text: "删除选中"
                md_bg_color: "#e74c3c"
                on_press: root.del_cart()

            MDRaisedButton:
                text: "清空报价单"
                md_bg_color: "#95a5a6"
                on_press: root.clear_cart()

            MDRaisedButton:
                text: "导出Excel"
                md_bg_color: "#9b59b6"
                on_press: root.export_quote_excel()
'''

# ==================== 界面类 ====================

class MainScreen(Screen):
    def show_admin_login(self):
        """显示管理员登录对话框"""
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
                    MDFlatButton(text="取消", on_press=lambda x: dialog.dismiss()),
                    MDRaisedButton(
                        text="确定",
                        on_press=lambda x: self.check_password(pwd_input.text, dialog)
                    )
                ]
            )
            dialog.open()
        except Exception as e:
            log_error(f"显示登录对话框失败: {traceback.format_exc()}")
            Snackbar(text=f"错误: {str(e)}", duration=3).open()

    def check_password(self, pwd, dialog):
        if pwd == ADMIN_PASSWORD:
            dialog.dismiss()
            self.manager.current = "admin"
        else:
            Snackbar(text="密码错误！", duration=2).open()


class ClientScreen(Screen):
    def on_enter(self):
        try:
            self.search_data()
        except Exception as e:
            log_error(f"ClientScreen.on_enter 错误: {traceback.format_exc()}")
            self.ids.tip_text.text = f"加载失败: {str(e)}"

    def search_data(self):
        try:
            key = self.ids.search_key.text.strip()
            self.ids.table_box.clear_widgets()
            self.ids.tip_text.text = ""

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            if key:
                c.execute(
                    "SELECT project_name, model_spec, measure_range, price FROM capabilities WHERE project_name LIKE ? ORDER BY project_name",
                    (f"%{key}%",)
                )
            else:
                c.execute("SELECT project_name, model_spec, measure_range, price FROM capabilities ORDER BY project_name")
            res = c.fetchall()
            conn.close()

            if not res:
                self.ids.tip_text.text = "暂不开展此项业务"
                return

            table = MDDataTable(
                size_hint=(1, None),
                height=dp(len(res) * 45 + 50),
                column_data=[
                    ("序号", dp(50)),
                    ("检定项目", dp(120)),
                    ("型号规格", dp(120)),
                    ("测量范围", dp(120)),
                    ("价格", dp(80))
                ],
                row_data=[(str(i+1), r[0], r[1], r[2], r[3]) for i, r in enumerate(res)]
            )
            self.ids.table_box.add_widget(table)

        except Exception as e:
            log_error(f"search_data 错误: {traceback.format_exc()}")
            self.ids.tip_text.text = f"查询错误: {str(e)}"


class AdminScreen(Screen):
    editing_id = None
    table = None

    def on_enter(self):
        try:
            self.load_list()
        except Exception as e:
            log_error(f"AdminScreen.on_enter 错误: {traceback.format_exc()}")
            Snackbar(text=f"加载失败: {str(e)}", duration=3).open()

    def load_list(self):
        try:
            self.ids.admin_table_box.clear_widgets()
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, project_name, model_spec, measure_range, price FROM capabilities ORDER BY id ASC")
            res = c.fetchall()
            conn.close()

            if not res:
                label = MDLabel(text="暂无数据", halign="center")
                self.ids.admin_table_box.add_widget(label)
                return

            table = MDDataTable(
                size_hint=(1, None),
                height=dp(len(res) * 45 + 50),
                column_data=[
                    ("ID", dp(40)),
                    ("项目", dp(100)),
                    ("型号", dp(100)),
                    ("范围", dp(100)),
                    ("价格", dp(70))
                ],
                row_data=[(str(r[0]), r[1], r[2], r[3], r[4]) for r in res],
                use_pagination=False,
                check=False
            )
            table.bind(on_row_press=self.on_row_select)
            self.ids.admin_table_box.add_widget(table)
            self.table = table

        except Exception as e:
            log_error(f"load_list 错误: {traceback.format_exc()}")
            Snackbar(text=f"加载失败: {str(e)}", duration=3).open()

    def on_row_select(self, instance_table, instance_row):
        pass

    def get_selected_row(self):
        if self.table is None:
            return None
        if hasattr(self.table, 'current_row') and self.table.current_row:
            return self.table.current_row
        return None

    def save_data(self):
        try:
            p1 = self.ids.e1.text.strip()
            p2 = self.ids.e2.text.strip()
            p3 = self.ids.e3.text.strip()
            p4 = self.ids.e4.text.strip()

            if not all([p1, p2, p3, p4]):
                Snackbar(text="所有字段不能为空！", duration=2).open()
                return

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            if self.editing_id:
                c.execute(
                    "UPDATE capabilities SET project_name=?, model_spec=?, measure_range=?, price=? WHERE id=?",
                    (p1, p2, p3, p4, self.editing_id)
                )
                self.editing_id = None
                self.ids.edit_tip.text = ""
                msg = "修改成功！"
            else:
                c.execute(
                    "INSERT INTO capabilities (project_name, model_spec, measure_range, price) VALUES (?,?,?,?)",
                    (p1, p2, p3, p4)
                )
                msg = "保存成功！"
            conn.commit()
            conn.close()

            self.clear_input()
            self.load_list()
            Snackbar(text=msg, duration=2).open()

        except Exception as e:
            log_error(f"save_data 错误: {traceback.format_exc()}")
            Snackbar(text=f"保存失败: {str(e)}", duration=3).open()

    def edit_data(self):
        try:
            row = self.get_selected_row()
            if not row:
                Snackbar(text="请选择一行数据！", duration=2).open()
                return

            self.editing_id = int(row[0])
            self.ids.e1.text = row[1]
            self.ids.e2.text = row[2]
            self.ids.e3.text = row[3]
            self.ids.e4.text = row[4]
            self.ids.edit_tip.text = f"正在修改 ID: {self.editing_id}"
        except Exception as e:
            log_error(f"edit_data 错误: {traceback.format_exc()}")
            Snackbar(text=f"操作失败: {str(e)}", duration=3).open()

    def del_data(self):
        try:
            row = self.get_selected_row()
            if not row:
                Snackbar(text="请选择一行数据！", duration=2).open()
                return

            dialog = MDDialog(
                title="确认删除",
                text=f"确定要删除 ID={row[0]} 的记录吗？",
                buttons=[
                    MDFlatButton(text="取消", on_press=lambda x: dialog.dismiss()),
                    MDRaisedButton(
                        text="确定删除",
                        md_bg_color="#e74c3c",
                        on_press=lambda x: self.confirm_delete(row[0], dialog)
                    )
                ]
            )
            dialog.open()
        except Exception as e:
            log_error(f"del_data 错误: {traceback.format_exc()}")
            Snackbar(text=f"操作失败: {str(e)}", duration=3).open()

    def confirm_delete(self, rid, dialog):
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM capabilities WHERE id=?", (rid,))
            conn.commit()
            conn.close()

            if self.editing_id == rid:
                self.clear_input()
                self.editing_id = None
                self.ids.edit_tip.text = ""

            dialog.dismiss()
            self.load_list()
            Snackbar(text="删除成功！", duration=2).open()

        except Exception as e:
            log_error(f"confirm_delete 错误: {traceback.format_exc()}")
            Snackbar(text=f"删除失败: {str(e)}", duration=3).open()

    def clear_input(self):
        self.ids.e1.text = ""
        self.ids.e2.text = ""
        self.ids.e3.text = ""
        self.ids.e4.text = ""

    def import_from_excel(self):
        """导入Excel文件"""
        try:
            from kivy.uix.filechooser import FileChooserListView
            from kivy.uix.popup import Popup

            content = BoxLayout(orientation='vertical')
            filechooser = FileChooserListView(
                path='/storage/emulated/0/Download/',
                filters=['*.xlsx']
            )
            content.add_widget(filechooser)

            btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
            cancel_btn = Button(text="取消", on_press=lambda x: popup.dismiss())
            confirm_btn = Button(text="导入", on_press=lambda x: self.process_import(filechooser.selection, popup))
            btn_layout.add_widget(cancel_btn)
            btn_layout.add_widget(confirm_btn)
            content.add_widget(btn_layout)

            popup = Popup(
                title="选择Excel文件",
                content=content,
                size_hint=(0.9, 0.8)
            )
            popup.open()
        except Exception as e:
            log_error(f"import_from_excel 错误: {traceback.format_exc()}")
            Snackbar(text=f"无法打开文件选择器: {str(e)}", duration=3).open()

    def process_import(self, selection, popup):
        if not selection:
            Snackbar(text="未选择文件！", duration=2).open()
            return

        file_path = selection[0]
        popup.dismiss()
        self.do_import(file_path)

    def do_import(self, file_path):
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active

            headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]

            mapping = {}
            for idx, h in enumerate(headers):
                if h in EXCEL_HEADERS:
                    mapping[h] = idx

            if len(mapping) != len(EXCEL_HEADERS):
                Snackbar(text="Excel表头格式不匹配！", duration=3).open()
                return

            col_idx = [mapping[h] for h in EXCEL_HEADERS]

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            count = 0
            skip = 0

            for row in ws.iter_rows(min_row=2, values_only=True):
                vals = [str(row[i]).strip() if row[i] is not None else "" for i in col_idx]
                if any(not v for v in vals):
                    skip += 1
                    continue
                c.execute(
                    "INSERT INTO capabilities (project_name, model_spec, measure_range, price) VALUES (?,?,?,?)",
                    vals
                )
                count += 1

            conn.commit()
            conn.close()
            self.load_list()

            msg = f"成功导入 {count} 条记录！"
            if skip:
                msg += f"\n跳过 {skip} 条不完整记录。"
            Snackbar(text=msg, duration=4).open()

        except Exception as e:
            log_error(f"do_import 错误: {traceback.format_exc()}")
            Snackbar(text=f"导入失败: {str(e)}", duration=3).open()


class QuoteScreen(Screen):
    cart_items = []
    q_table = None
    cart_table = None

    def on_enter(self):
        try:
            self.q_search()
            self.refresh_cart()
        except Exception as e:
            log_error(f"QuoteScreen.on_enter 错误: {traceback.format_exc()}")
            Snackbar(text=f"加载失败: {str(e)}", duration=3).open()

    def q_search(self):
        try:
            key = self.ids.q_search.text.strip()
            self.ids.q_table_box.clear_widgets()

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            if key:
                c.execute(
                    "SELECT project_name, model_spec, measure_range, price FROM capabilities WHERE project_name LIKE ? ORDER BY project_name",
                    (f"%{key}%",)
                )
            else:
                c.execute("SELECT project_name, model_spec, measure_range, price FROM capabilities ORDER BY project_name")
            res = c.fetchall()
            conn.close()

            if not res:
                label = MDLabel(text="暂无数据", halign="center")
                self.ids.q_table_box.add_widget(label)
                return

            table = MDDataTable(
                size_hint=(1, None),
                height=dp(len(res) * 45 + 50),
                column_data=[
                    ("项目", dp(100)),
                    ("型号", dp(100)),
                    ("范围", dp(100)),
                    ("价格", dp(70))
                ],
                row_data=res,
                check=False
            )
            self.ids.q_table_box.add_widget(table)
            self.q_table = table

        except Exception as e:
            log_error(f"q_search 错误: {traceback.format_exc()}")
            Snackbar(text=f"查询失败: {str(e)}", duration=2).open()

    def get_selected_quote_row(self):
        if self.q_table is None:
            return None
        if hasattr(self.q_table, 'current_row') and self.q_table.current_row:
            return self.q_table.current_row
        return None

    def add_cart(self):
        try:
            row = self.get_selected_quote_row()
            if not row:
                Snackbar(text="请先搜索并选择项目！", duration=2).open()
                return

            try:
                qty = float(self.ids.qty_input.text.strip())
                if qty <= 0:
                    raise ValueError
            except:
                Snackbar(text="数量必须是正数！", duration=2).open()
                return

            price_num = parse_price(row[3])
            subtotal = price_num * qty

            self.cart_items.append({
                "project_name": row[0],
                "model_spec": row[1],
                "measure_range": row[2],
                "price_str": row[3],
                "unit_price": price_num,
                "quantity": qty,
                "subtotal": subtotal
            })

            self.refresh_cart()

        except Exception as e:
            log_error(f"add_cart 错误: {traceback.format_exc()}")
            Snackbar(text=f"操作失败: {str(e)}", duration=3).open()

    def refresh_cart(self):
        try:
            self.ids.cart_box.clear_widgets()

            if not self.cart_items:
                self.ids.total_text.text = "总金额：0.00 元"
                return

            rows = []
            total = 0
            for item in self.cart_items:
                rows.append((
                    item["project_name"],
                    item["model_spec"],
                    item["measure_range"],
                    item["price_str"],
                    str(item["quantity"]),
                    f"{item['subtotal']:.2f}"
                ))
                total += item["subtotal"]

            table = MDDataTable(
                size_hint=(1, None),
                height=dp(len(rows) * 45 + 50),
                column_data=[
                    ("项目", dp(80)),
                    ("型号", dp(80)),
                    ("范围", dp(80)),
                    ("单价", dp(50)),
                    ("数量", dp(40)),
                    ("小计", dp(60))
                ],
                row_data=rows,
                check=False
            )
            self.ids.cart_box.add_widget(table)
            self.cart_table = table
            self.ids.total_text.text = f"总金额：{total:.2f} 元"

        except Exception as e:
            log_error(f"refresh_cart 错误: {traceback.format_exc()}")

    def get_selected_cart_row(self):
        if self.cart_table is None:
            return None
        if hasattr(self.cart_table, 'current_row') and self.cart_table.current_row:
            return self.cart_table.current_row
        return None

    def del_cart(self):
        try:
            row = self.get_selected_cart_row()
            if not row:
                Snackbar(text="请选择要删除的项目！", duration=2).open()
                return

            for i, item in enumerate(self.cart_items):
                if item["project_name"] == row[0] and item["model_spec"] == row[1]:
                    del self.cart_items[i]
                    break

            self.refresh_cart()

        except Exception as e:
            log_error(f"del_cart 错误: {traceback.format_exc()}")
            Snackbar(text=f"操作失败: {str(e)}", duration=3).open()

    def clear_cart(self):
        if not self.cart_items:
            return

        dialog = MDDialog(
            title="确认清空",
            text="确定清空当前报价单吗？",
            buttons=[
                MDFlatButton(text="取消", on_press=lambda x: dialog.dismiss()),
                MDRaisedButton(
                    text="确定清空",
                    md_bg_color="#e74c3c",
                    on_press=lambda x: self.do_clear_cart(dialog)
                )
            ]
        )
        dialog.open()

    def do_clear_cart(self, dialog):
        self.cart_items.clear()
        self.refresh_cart()
        dialog.dismiss()
        Snackbar(text="报价单已清空", duration=2).open()

    def export_quote_excel(self):
        try:
            if not self.cart_items:
                Snackbar(text="报价单为空！", duration=2).open()
                return

            # Android 环境下保存到下载目录
            try:
                from android.storage import primary_external_storage_path
                save_dir = os.path.join(primary_external_storage_path(), 'Download')
            except:
                save_dir = '/storage/emulated/0/Download'

            if not os.path.exists(save_dir):
                try:
                    from android.storage import app_storage_path
                    save_dir = app_storage_path()
                except:
                    save_dir = os.getcwd()

            from datetime import datetime
            filename = f"报价单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = os.path.join(save_dir, filename)

            wb = Workbook()
            ws = wb.active
            ws.title = "报价单"

            # 标题
            ws.merge_cells("A1:F1")
            ws["A1"] = "检校业务报价单"
            ws["A1"].font = Font(name="微软雅黑", size=16, bold=True)
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 35

            # 表头
            headers = ["检定项目", "型号规格", "测量范围", "单价", "数量", "小计"]
            header_fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
            header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style="thin"), right=Side(style="thin"),
                top=Side(style="thin"), bottom=Side(style="thin")
            )

            for col, h in enumerate(headers, 1):
                cell = ws.cell(row=2, column=col, value=h)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border

            # 数据行
            for row_idx, item in enumerate(self.cart_items, 3):
                row_data = [
                    item["project_name"],
                    item["model_spec"],
                    item["measure_range"],
                    item["price_str"],
                    item["quantity"],
                    item["subtotal"]
                ]
                for col_idx, val in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.font = Font(name="微软雅黑", size=11)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = thin_border

            # 合计行
            total_row = len(self.cart_items) + 3
            ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=5)
            cell = ws.cell(row=total_row, column=1, value="合计")
            cell.font = Font(name="微软雅黑", size=11, bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

            total = sum(item["subtotal"] for item in self.cart_items)
            total_cell = ws.cell(row=total_row, column=6, value=total)
            total_cell.font = Font(name="微软雅黑", size=11, bold=True)
            total_cell.alignment = Alignment(horizontal="center", vertical="center")
            total_cell.border = thin_border

            # 调整