#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准仪器维检部检校业务价格查询系统 - 纯Kivy版（安卓适配）
不使用 KivyMD，全部用原生 Kivy 组件
Excel导入固定格式：
- 支持 .xlsx 格式
- 第一行为表头，列名为：检定项目、型号规格、测量范围、价格
- 从第二行开始为数据行
"""
import os
import sys
import re
import sqlite3
import shutil

# ==================== 安卓环境检测 ====================
ANDROID = 'ANDROID_ARGUMENT' in os.environ

# ==================== 路径配置 ====================
if ANDROID:
    # 安卓外部存储路径
    from android.storage import primary_external_storage_path
    BASE_DIR = primary_external_storage_path()
    DB_NAME = os.path.join(BASE_DIR, "business.db")
    # 安卓上需要申请存储权限
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except Exception:
        pass
else:
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_NAME = os.path.join(BASE_DIR, "business.db")

# 打包后的资源路径（PyInstaller/Buildozer 单文件模式解压目录）
MEIPASS_DIR = getattr(sys, '_MEIPASS', BASE_DIR)

ADMIN_PASSWORD = "432"
EXCEL_HEADERS = ["检定项目", "型号规格", "测量范围", "价格"]


def parse_price(price_str):
    """从价格字符串中提取数字"""
    nums = re.findall(r'\d+\.?\d*', str(price_str))
    if nums:
        return float(nums[0])
    return 0.0


def ensure_db():
    """确保数据库文件存在"""
    db_dir = os.path.dirname(DB_NAME)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    if not os.path.exists(DB_NAME):
        bundled_db = os.path.join(MEIPASS_DIR, "business.db")
        if os.path.exists(bundled_db):
            shutil.copy2(bundled_db, DB_NAME)


def init_db():
    """初始化数据库"""
    ensure_db()
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


# ==================== Kivy 导入 ====================
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.widget import Widget

# ==================== 注册中文字体 ====================
FONT_NAME = "ChineseFont"
try:
    from kivy.resources import resource_add_path
    resource_add_path(BASE_DIR)
    # 尝试多种字体文件名
    font_candidates = [
        "NotoSansSC-Regular.otf",
        "NotoSerifCJKsc-Regular.otf",
        "NotoSansCJK-Regular.ttc",
        "simhei.ttf",
        "msyh.ttf",
    ]
    font_loaded = False
    for fname in font_candidates:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            LabelBase.register(name=FONT_NAME, fn_regular=fpath)
            font_loaded = True
            break
    if not font_loaded:
        # 找不到自定义字体，用默认
        FONT_NAME = "Roboto"
except Exception:
    FONT_NAME = "Roboto"


# ==================== 导入 openpyxl ====================
try:
    from openpyxl import load_workbook, Workbook
    from openpyxl.styles import Font as XLFont, Alignment as XLAlign, Border as XLBorder, Side as XLSide, PatternFill
    HAS_OPENPYXL = True
except Exception:
    HAS_OPENPYXL = False


# ==================== 自定义控件 ====================
class HBox(BoxLayout):
    """水平盒子"""
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        super().__init__(**kwargs)


class VBox(BoxLayout):
    """垂直盒子"""
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        super().__init__(**kwargs)


class TableRow(BoxLayout):
    """表格行：带背景色"""
    def __init__(self, bg_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class DataTable(GridLayout):
    """简易表格：自动填充数据"""
    headers = ListProperty([])
    rows_data = ListProperty([])
    selected_index = NumericProperty(-1)
    on_row_click = None  # 回调函数

    def __init__(self, **kwargs):
        self.headers = kwargs.pop('headers', [])
        self.cols = len(self.headers) if self.headers else 1
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.row_height = dp(40)
        self.header_height = dp(45)

    def set_data(self, rows_data, selectable=True):
        """设置表格数据"""
        self.rows_data = rows_data
        self.selected_index = -1
        self.selectable = selectable
        self.refresh_table()

    def refresh_table(self):
        self.clear_widgets()
        # 表头
        if self.headers:
            h_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=self.header_height)
            with h_row.canvas.before:
                Color(0.17, 0.22, 0.31, 1)  # 深蓝灰
                Rectangle(pos=h_row.pos, size=h_row.size)
            for i, h in enumerate(self.headers):
                lbl = Label(
                    text=str(h),
                    font_name=FONT_NAME,
                    font_size=sp(14) if not ANDROID else sp(12),
                    color=(1, 1, 1, 1),
                    bold=True,
                    halign='center',
                    valign='middle',
                    text_size=(None, None),
                )
                h_row.add_widget(lbl)
            self.add_widget(h_row)

        # 数据行
        for idx, row in enumerate(self.rows_data):
            bg = (0.95, 0.95, 0.95, 1) if idx % 2 == 0 else (1, 1, 1, 1)
            if idx == self.selected_index:
                bg = (0.2, 0.6, 1, 0.3)
            row_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=self.row_height,
            )
            with row_box.canvas.before:
                Color(*bg)
                Rectangle(pos=row_box.pos, size=row_box.size)

            for cell in row:
                lbl = Label(
                    text=str(cell),
                    font_name=FONT_NAME,
                    font_size=sp(13) if not ANDROID else sp(11),
                    color=(0.1, 0.1, 0.1, 1),
                    halign='center',
                    valign='middle',
                    text_size=(None, None),
                )
                row_box.add_widget(lbl)

            if self.selectable:
                row_idx = idx
                def on_touch_down(instance, touch, ri=row_idx):
                    if instance.collide_point(*touch.pos):
                        self.selected_index = ri
                        self.refresh_table()
                        if self.on_row_click:
                            self.on_row_click(ri)
                        return True
                row_box.bind(on_touch_down=on_touch_down)

            self.add_widget(row_box)


def sp(size):
    """缩放像素"""
    from kivy.metrics import sp as _sp
    return _sp(size)


# ==================== 弹窗工具 ====================
def show_message(title, text, msg_type='info'):
    """显示消息弹窗"""
    bg_color = {
        'info': (0.15, 0.55, 0.8, 1),
        'error': (0.76, 0.23, 0.18, 1),
        'warning': (0.95, 0.77, 0.06, 1),
    }.get(msg_type, (0.2, 0.6, 0.35, 1))

    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    content.add_widget(Label(
        text=text,
        font_name=FONT_NAME,
        font_size=sp(14),
        halign='center',
        valign='middle',
        text_size=(dp(280), None),
    ))
    btn = Button(
        text='确定',
        font_name=FONT_NAME,
        size_hint_y=None,
        height=dp(40),
        background_color=bg_color,
        color=(1, 1, 1, 1),
    )
    content.add_widget(btn)
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    btn.bind(on_press=popup.dismiss)
    popup.open()
    return popup


def show_confirm(title, text, on_yes):
    """确认弹窗"""
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    content.add_widget(Label(
        text=text,
        font_name=FONT_NAME,
        font_size=sp(14),
        halign='center',
        valign='middle',
        text_size=(dp(280), None),
    ))
    btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
    btn_yes = Button(
        text='确定',
        font_name=FONT_NAME,
        background_color=(0.76, 0.23, 0.18, 1),
        color=(1, 1, 1, 1),
    )
    btn_no = Button(
        text='取消',
        font_name=FONT_NAME,
        background_color=(0.6, 0.6, 0.6, 1),
        color=(1, 1, 1, 1),
    )
    btns.add_widget(btn_yes)
    btns.add_widget(btn_no)
    content.add_widget(btns)
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
    btn_no.bind(on_press=popup.dismiss)
    btn_yes.bind(on_press=lambda x: (popup.dismiss(), on_yes()))
    popup.open()


# ==================== 页面类 ====================
class MainScreen(Screen):
    """首页"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        layout.add_widget(Label(
            text="标准仪器维检部",
            font_name=FONT_NAME,
            font_size=sp(28),
            bold=True,
            size_hint_y=None,
            height=dp(60),
        ))
        layout.add_widget(Label(
            text="检校业务价格查询系统",
            font_name=FONT_NAME,
            font_size=sp(20),
            size_hint_y=None,
            height=dp(50),
        ))

        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        btn_client = Button(
            text="单价查询",
            font_name=FONT_NAME,
            font_size=sp(16),
            size_hint_y=None,
            height=dp(55),
            background_color=(0.16, 0.5, 0.73, 1),
            color=(1, 1, 1, 1),
        )
        btn_client.bind(on_press=lambda x: setattr(self.manager, 'current', 'client'))
        layout.add_widget(btn_client)

        btn_quote = Button(
            text="批量报价",
            font_name=FONT_NAME,
            font_size=sp(16),
            size_hint_y=None,
            height=dp(55),
            background_color=(0.56, 0.27, 0.67, 1),
            color=(1, 1, 1, 1),
        )
        btn_quote.bind(on_press=lambda x: setattr(self.manager, 'current', 'quote'))
        layout.add_widget(btn_quote)

        btn_admin = Button(
            text="管理入口",
            font_name=FONT_NAME,
            font_size=sp(16),
            size_hint_y=None,
            height=dp(55),
            background_color=(0.75, 0.24, 0.16, 1),
            color=(1, 1, 1, 1),
        )
        btn_admin.bind(on_press=self.show_admin_login)
        layout.add_widget(btn_admin)

        self.add_widget(layout)

    def show_admin_login(self, *args):
        """弹出密码输入框"""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text="请输入管理员密码：",
            font_name=FONT_NAME,
            font_size=sp(14),
            size_hint_y=None,
            height=dp(40),
        ))
        pwd_input = TextInput(
            password=True,
            multiline=False,
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(45),
        )
        content.add_widget(pwd_input)
        btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_ok = Button(
            text="确定",
            font_name=FONT_NAME,
            background_color=(0.15, 0.55, 0.35, 1),
            color=(1, 1, 1, 1),
        )
        btn_cancel = Button(
            text="取消",
            font_name=FONT_NAME,
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1),
        )
        btns.add_widget(btn_cancel)
        btns.add_widget(btn_ok)
        content.add_widget(btns)

        popup = Popup(title="管理员验证", content=content, size_hint=(0.8, 0.4))
        btn_cancel.bind(on_press=popup.dismiss)

        def check(*args):
            if pwd_input.text == ADMIN_PASSWORD:
                popup.dismiss()
                self.manager.current = "admin"
            else:
                show_message("错误", "密码错误！", "error")

        btn_ok.bind(on_press=check)
        popup.open()


class ClientScreen(Screen):
    """单价查询页"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "client"
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))

        # 顶部栏
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_back = Button(
            text="← 返回",
            font_name=FONT_NAME,
            size_hint_x=0.25,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        title = Label(
            text="单价查询",
            font_name=FONT_NAME,
            font_size=sp(18),
            bold=True,
        )
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        root.add_widget(top_bar)

        # 搜索栏
        search_bar = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        self.search_input = TextInput(
            hint_text="输入检定项目搜索",
            multiline=False,
            font_name=FONT_NAME,
            size_hint_x=0.7,
        )
        btn_search = Button(
            text="查询",
            font_name=FONT_NAME,
            size_hint_x=0.3,
            background_color=(0.16, 0.5, 0.73, 1),
            color=(1, 1, 1, 1),
        )
        btn_search.bind(on_press=self.do_search)
        self.search_input.bind(on_text_validate=self.do_search)
        search_bar.add_widget(self.search_input)
        search_bar.add_widget(btn_search)
        root.add_widget(search_bar)

        # 提示文字
        self.tip_label = Label(
            text="",
            font_name=FONT_NAME,
            font_size=sp(14),
            color=(0.76, 0.23, 0.18, 1),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(self.tip_label)

        # 结果表格（ScrollView 包裹）
        scroll = ScrollView(size_hint=(1, 1))
        self.result_table = DataTable(
            headers=["序号", "检定项目", "型号规格", "测量范围", "价格"],
        )
        self.result_table.row_height = dp(45)
        scroll.add_widget(self.result_table)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_enter(self):
        """进入页面时自动加载全部数据"""
        self.do_search()

    def do_search(self, *args):
        keyword = self.search_input.text.strip()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if keyword:
            c.execute(
                """SELECT project_name, model_spec, measure_range, price
                   FROM capabilities
                   WHERE project_name LIKE ?
                   ORDER BY project_name""",
                (f"%{keyword}%",)
            )
        else:
            c.execute(
                "SELECT project_name, model_spec, measure_range, price FROM capabilities ORDER BY project_name"
            )
        rows = c.fetchall()
        conn.close()

        if not rows:
            self.tip_label.text = "暂不开展此项业务"
            self.result_table.set_data([])
        else:
            self.tip_label.text = ""
            table_rows = []
            for i, row in enumerate(rows, 1):
                table_rows.append((i,) + row)
            self.result_table.set_data(table_rows, selectable=False)


class AdminScreen(Screen):
    """管理后台"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin"
        self.editing_id = None
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))

        # 顶部栏
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_back = Button(
            text="← 返回",
            font_name=FONT_NAME,
            size_hint_x=0.25,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        title = Label(
            text="管理后台",
            font_name=FONT_NAME,
            font_size=sp(18),
            bold=True,
        )
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        root.add_widget(top_bar)

        # 滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # 输入表单
        self.entries = []
        labels = ["检定项目", "型号规格", "测量范围", "价格"]
        for lbl_text in labels:
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
            row.add_widget(Label(
                text=lbl_text + "：",
                font_name=FONT_NAME,
                size_hint_x=0.3,
                halign='right',
            ))
            ti = TextInput(
                multiline=False,
                font_name=FONT_NAME,
                size_hint_x=0.7,
            )
            row.add_widget(ti)
            self.entries.append(ti)
            content.add_widget(row)

        # 编辑状态提示
        self.edit_tip = Label(
            text="",
            font_name=FONT_NAME,
            font_size=sp(12),
            color=(0.95, 0.6, 0.04, 1),
            size_hint_y=None,
            height=dp(25),
        )
        content.add_widget(self.edit_tip)

        # 按钮组 1
        btn_row1 = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        btn_save = Button(
            text="保存",
            font_name=FONT_NAME,
            background_color=(0.15, 0.68, 0.4, 1),
            color=(1, 1, 1, 1),
        )
        btn_save.bind(on_press=self.save_record)
        btn_edit = Button(
            text="修改",
            font_name=FONT_NAME,
            background_color=(0.95, 0.6, 0.04, 1),
            color=(1, 1, 1, 1),
        )
        btn_edit.bind(on_press=self.edit_record)
        btn_del = Button(
            text="删除",
            font_name=FONT_NAME,
            background_color=(0.91, 0.3, 0.24, 1),
            color=(1, 1, 1, 1),
        )
        btn_del.bind(on_press=self.delete_record)
        btn_row1.add_widget(btn_save)
        btn_row1.add_widget(btn_edit)
        btn_row1.add_widget(btn_del)
        content.add_widget(btn_row1)

        # 按钮组 2
        btn_row2 = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        btn_refresh = Button(
            text="刷新列表",
            font_name=FONT_NAME,
            background_color=(0.2, 0.6, 0.85, 1),
            color=(1, 1, 1, 1),
        )
        btn_refresh.bind(on_press=self.load_list)
        btn_import = Button(
            text="导入Excel",
            font_name=FONT_NAME,
            background_color=(0.6, 0.35, 0.75, 1),
            color=(1, 1, 1, 1),
        )
        btn_import.bind(on_press=self.import_from_excel)
        btn_row2.add_widget(btn_refresh)
        btn_row2.add_widget(btn_import)
        content.add_widget(btn_row2)

        # 列表标题
        content.add_widget(Label(
            text="数据列表（点击选中）",
            font_name=FONT_NAME,
            font_size=sp(14),
            bold=True,
            size_hint_y=None,
            height=dp(28),
        ))

        # 数据表格
        self.admin_table = DataTable(
            headers=["ID", "检定项目", "型号规格", "测量范围", "价格"],
        )
        self.admin_table.row_height = dp(40)
        self.admin_table.on_row_click = self.on_table_select
        content.add_widget(self.admin_table)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.load_list()

    def on_table_select(self, index):
        """选中表格行"""
        if 0 <= index < len(self.admin_table.rows_data):
            row = self.admin_table.rows_data[index]
            self.editing_id = int(row[0])
            # 填充输入框
            for i, entry in enumerate(self.entries):
                entry.text = str(row[i + 1])
            self.edit_tip.text = f"正在修改 ID={self.editing_id} 的记录"

    def load_list(self, *args):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, project_name, model_spec, measure_range, price FROM capabilities ORDER BY id ASC")
        rows = c.fetchall()
        conn.close()
        self.admin_table.set_data(rows)

    def save_record(self, *args):
        vals = [e.text.strip() for e in self.entries]
        if any(not v for v in vals):
            show_message("提示", "所有字段都必须填写！", "warning")
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if self.editing_id is not None:
            c.execute(
                "UPDATE capabilities SET project_name=?, model_spec=?, measure_range=?, price=? WHERE id=?",
                (*vals, self.editing_id)
            )
            msg = "信息已修改！"
        else:
            c.execute(
                "INSERT INTO capabilities (project_name, model_spec, measure_range, price) VALUES (?,?,?,?)",
                vals
            )
            msg = "信息已保存！"
        conn.commit()
        conn.close()
        for e in self.entries:
            e.text = ""
        self.editing_id = None
        self.edit_tip.text = ""
        self.load_list()
        show_message("成功", msg)

    def edit_record(self, *args):
        if self.admin_table.selected_index < 0:
            show_message("提示", "请先在列表中选中要修改的记录！", "warning")
            return
        row = self.admin_table.rows_data[self.admin_table.selected_index]
        self.editing_id = int(row[0])
        for i, entry in enumerate(self.entries):
            entry.text = str(row[i + 1])
        self.edit_tip.text = f"正在修改 ID={self.editing_id} 的记录，修改后点保存"

    def delete_record(self, *args):
        if self.admin_table.selected_index < 0:
            show_message("提示", "请先在列表中选中要删除的记录！", "warning")
            return
        row = self.admin_table.rows_data[self.admin_table.selected_index]
        rid = int(row[0])

        def do_delete():
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM capabilities WHERE id=?", (rid,))
            conn.commit()
            conn.close()
            if self.editing_id == rid:
                for e in self.entries:
                    e.text = ""
                self.editing_id = None
                self.edit_tip.text = ""
            self.load_list()

        show_confirm("确认", f"确定删除 ID={rid} 的记录吗？", do_delete)

    def import_from_excel(self, *args):
        if not HAS_OPENPYXL:
            show_message("错误", "openpyxl 未安装，无法导入Excel！", "error")
            return

        # 文件选择
        content = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(5))
        fc = FileChooserListView(path=BASE_DIR, filters=['*.xlsx'])
        content.add_widget(fc)
        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        btn_ok = Button(text="选择", font_name=FONT_NAME, background_color=(0.15, 0.68, 0.4, 1), color=(1, 1, 1, 1))
        btn_cancel = Button(text="取消", font_name=FONT_NAME, background_color=(0.6, 0.6, 0.6, 1), color=(1, 1, 1, 1))
        btn_row.add_widget(btn_cancel)
        btn_row.add_widget(btn_ok)
        content.add_widget(btn_row)
        popup = Popup(title="选择Excel文件", content=content, size_hint=(0.95, 0.8))
        btn_cancel.bind(on_press=popup.dismiss)

        def do_import(*args):
            if not fc.selection:
                return
            file_path = fc.selection[0]
            popup.dismiss()
            self._do_excel_import(file_path)

        btn_ok.bind(on_press=do_import)
        popup.open()

    def _do_excel_import(self, file_path):
        try:
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active
            headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            mapping = {}
            for idx, h in enumerate(headers):
                if h in EXCEL_HEADERS:
                    mapping[h] = idx
            if len(mapping) != len(EXCEL_HEADERS):
                show_message(
                    "格式错误",
                    f"表头应为：{EXCEL_HEADERS}",
                    "error"
                )
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
            info = f"成功导入 {count} 条记录！"
            if skip:
                info += f"\n跳过 {skip} 条空记录。"
            show_message("导入成功", info)
        except Exception as e:
            show_message("导入失败", f"读取Excel出错：\n{e}", "error")


class QuoteScreen(Screen):
    """批量报价页"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "quote"
        self.quote_items = []
        self.selected_result_index = -1
        self.selected_cart_index = -1
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))

        # 顶部栏
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_back = Button(
            text="← 返回",
            font_name=FONT_NAME,
            size_hint_x=0.25,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        title = Label(
            text="批量报价",
            font_name=FONT_NAME,
            font_size=sp(18),
            bold=True,
        )
        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        root.add_widget(top_bar)

        # 搜索栏
        search_bar = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.q_search = TextInput(
            hint_text="搜索检定项目",
            multiline=False,
            font_name=FONT_NAME,
            size_hint_x=0.7,
        )
        btn_qsearch = Button(
            text="搜索",
            font_name=FONT_NAME,
            size_hint_x=0.3,
            background_color=(0.16, 0.5, 0.73, 1),
            color=(1, 1, 1, 1),
        )
        btn_qsearch.bind(on_press=self.do_quote_search)
        self.q_search.bind(on_text_validate=self.do_quote_search)
        search_bar.add_widget(self.q_search)
        search_bar.add_widget(btn_qsearch)
        root.add_widget(search_bar)

        # 查询结果标题
        root.add_widget(Label(
            text="查询结果（点击选中）",
            font_name=FONT_NAME,
            font_size=sp(13),
            bold=True,
            size_hint_y=None,
            height=dp(25),
        ))

        # 查询结果表格
        scroll1 = ScrollView(size_hint=(1, 0.28))
        self.result_table = DataTable(
            headers=["序号", "检定项目", "型号规格", "测量范围", "价格"],
        )
        self.result_table.row_height = dp(38)
        self.result_table.on_row_click = self.on_result_select
        scroll1.add_widget(self.result_table)
        root.add_widget(scroll1)

        # 数量 + 加入报价单
        add_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        add_row.add_widget(Label(text="数量：", font_name=FONT_NAME, size_hint_x=0.25))
        self.qty_input = TextInput(
            text="1",
            multiline=False,
            input_filter='float',
            font_name=FONT_NAME,
            size_hint_x=0.3,
        )
        btn_add = Button(
            text="加入报价单",
            font_name=FONT_NAME,
            size_hint_x=0.45,
            background_color=(0.15, 0.68, 0.4, 1),
            color=(1, 1, 1, 1),
        )
        btn_add.bind(on_press=self.add_to_cart)
        add_row.add_widget(self.qty_input)
        add_row.add_widget(btn_add)
        root.add_widget(add_row)

        # 报价单标题
        root.add_widget(Label(
            text="报价单列表（点击选中删除）",
            font_name=FONT_NAME,
            font_size=sp(13),
            bold=True,
            size_hint_y=None,
            height=dp(25),
        ))

        # 报价单表格
        scroll2 = ScrollView(size_hint=(1, 0.28))
        self.cart_table = DataTable(
            headers=["检定项目", "型号规格", "测量范围", "单价", "数量", "小计"],
        )
        self.cart_table.row_height = dp(36)
        self.cart_table.on_row_click = self.on_cart_select
        scroll2.add_widget(self.cart_table)
        root.add_widget(scroll2)

        # 总金额
        self.total_label = Label(
            text="总金额：0.00 元",
            font_name=FONT_NAME,
            font_size=sp(18),
            bold=True,
            color=(0.75, 0.24, 0.16, 1),
            size_hint_y=None,
            height=dp(40),
        )
        root.add_widget(self.total_label)

        # 操作按钮
        btn_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        btn_del = Button(
            text="删除选中",
            font_name=FONT_NAME,
            background_color=(0.91, 0.3, 0.24, 1),
            color=(1, 1, 1, 1),
        )
        btn_del.bind(on_press=self.del_cart)
        btn_clear = Button(
            text="清空",
            font_name=FONT_NAME,
            background_color=(0.58, 0.64, 0.65, 1),
            color=(1, 1, 1, 1),
        )
        btn_clear.bind(on_press=self.clear_cart)
        btn_export = Button(
            text="导出Excel",
            font_name=FONT_NAME,
            background_color=(0.6, 0.35, 0.75, 1),
            color=(1, 1, 1, 1),
        )
        btn_export.bind(on_press=self.export_excel)
        btn_row.add_widget(btn_del)
        btn_row.add_widget(btn_clear)
        btn_row.add_widget(btn_export)
        root.add_widget(btn_row)

        # 返回查询页
        btn_back2 = Button(
            text="返回查询页",
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(35),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
        )
        btn_back2.bind(on_press=lambda x: setattr(self.manager, 'current', 'client'))
        root.add_widget(btn_back2)

        self.add_widget(root)

    def on_enter(self):
        self.do_quote_search()

    def on_result_select(self, index):
        self.selected_result_index = index

    def on_cart_select(self, index):
        self.selected_cart_index = index

    def do_quote_search(self, *args):
        keyword = self.q_search.text.strip()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if keyword:
            c.execute(
                """SELECT project_name, model_spec, measure_range, price
                   FROM capabilities
                   WHERE project_name LIKE ?
                   ORDER BY project_name""",
                (f"%{keyword}%",)
            )
        else:
            c.execute(
                "SELECT project_name, model_spec, measure_range, price FROM capabilities ORDER BY project_name"
            )
        rows = c.fetchall()
        conn.close()
        table_rows = [(i,) + row for i, row in enumerate(rows, 1)]
        self.result_table.set_data(table_rows)
        self.selected_result_index = -1

    def add_to_cart(self, *args):
        if self.selected_result_index < 0 or self.selected_result_index >= len(self.result_table.rows_data):
            show_message("提示", "请先从查询结果中选中一条记录！", "warning")
            return
        row = self.result_table.rows_data[self.selected_result_index]
        project_name = row[1]
        model_spec = row[2]
        measure_range = row[3]
        price_str = str(row[4])

        qty_str = self.qty_input.text.strip()
        try:
            qty = float(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            show_message("提示", "数量必须为正数！", "warning")
            return

        unit_price = parse_price(price_str)
        subtotal = unit_price * qty
        self.quote_items.append({
            "project_name": project_name,
            "model_spec": model_spec,
            "measure_range": measure_range,
            "price_str": price_str,
            "unit_price": unit_price,
            "quantity": qty,
            "subtotal": subtotal,
        })
        self.refresh_cart()

    def del_cart(self, *args):
        if self.selected_cart_index < 0 or self.selected_cart_index >= len(self.quote_items):
            show_message("提示", "请先选中报价单中的记录！", "warning")
            return
        idx = self.selected_cart_index

        def do_del():
            del self.quote_items[idx]
            self.selected_cart_index = -1
            self.refresh_cart()

        show_confirm("确认", "确定删除选中的报价项吗？", do_del)

    def clear_cart(self, *args):
        if not self.quote_items:
            return

        def do_clear():
            self.quote_items.clear()
            self.selected_cart_index = -1
            self.refresh_cart()

        show_confirm("确认", "确定清空当前报价单吗？", do_clear)

    def refresh_cart(self):
        rows = []
        total = 0.0
        for item in self.quote_items:
            rows.append((
                item["project_name"],
                item["model_spec"],
                item["measure_range"],
                item["price_str"],
                item["quantity"],
                f"{item['subtotal']:.2f}",
            ))
            total += item["subtotal"]
        self.cart_table.set_data(rows)
        self.total_label.text = f"总金额：{total:.2f} 元"

    def export_excel(self, *args):
        if not self.quote_items:
            show_message("提示", "报价单为空，无法导出！", "warning")
            return
        if not HAS_OPENPYXL:
            show_message("错误", "openpyxl 未安装！", "error")
            return

        # 安卓上直接保存到外部存储
        if ANDROID:
            filename = os.path.join(BASE_DIR, f"报价单_{len(self.quote_items)}项.xlsx")
            self._write_excel(filename)
        else:
            # PC 端用文件保存对话框
            content = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(5))
            filename_input = TextInput(
                text=f"报价单_{len(self.quote_items)}项.xlsx",
                multiline=False,
                font_name=FONT_NAME,
                size_hint_y=None,
                height=dp(40),
            )
            content.add_widget(Label(text="文件名：", font_name=FONT_NAME, size_hint_y=None, height=dp(30)))
            content.add_widget(filename_input)
            btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
            btn_ok = Button(text="保存", font_name=FONT_NAME, background_color=(0.15, 0.68, 0.4, 1), color=(1, 1, 1, 1))
            btn_cancel = Button(text="取消", font_name=FONT_NAME, background_color=(0.6, 0.6, 0.6, 1), color=(1, 1, 1, 1))
            btn_row.add_widget(btn_cancel)
            btn_row.add_widget(btn_ok)
            content.add_widget(btn_row)
            popup = Popup(title="保存报价单", content=content, size_hint=(0.8, 0.35))
            btn_cancel.bind(on_press=popup.dismiss)

            def do_save(*args):
                fname = filename_input.text.strip()
                if not fname.endswith('.xlsx'):
                    fname += '.xlsx'
                popup.dismiss()
                self._write_excel(os.path.join(BASE_DIR, fname))

            btn_ok.bind(on_press=do_save)
            popup.open()

    def _write_excel(self, file_path):
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "报价单"
            # 标题
            ws.merge_cells("A1:F1")
            ws["A1"] = "检校业务报价单"
            ws["A1"].font = XLFont(name="微软雅黑", size=16, bold=True)
            ws["A1"].alignment = XLAlign(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 35
            # 表头
            headers = ["检定项目", "型号规格", "测量范围", "单价", "数量", "小计"]
            header_fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
            header_font = XLFont(name="微软雅黑", size=11, bold=True, color="FFFFFF")
            thin_border = XLBorder(
                left=XLSide(style="thin"), right=XLSide(style="thin"),
                top=XLSide(style="thin"), bottom=XLSide(style="thin")
            )
            for col, h in enumerate(headers, 1):
                cell = ws.cell(row=2, column=col, value=h)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = XLAlign(horizontal="center", vertical="center")
                cell.border = thin_border
            # 数据
            for row_idx, item in enumerate(self.quote_items, 3):
                row_data = [
                    item["project_name"],
                    item["model_spec"],
                    item["measure_range"],
                    item["price_str"],
                    item["quantity"],
                    item["subtotal"],
                ]
                for col_idx, val in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=val)
                    cell.font = XLFont(name="微软雅黑", size=11)
                    cell.alignment = XLAlign(horizontal="center", vertical="center")
                    cell.border = thin_border
            # 合计
            total_row = len(self.quote_items) + 3
            ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=5)
            cell = ws.cell(row=total_row, column=1, value="合计")
            cell.font = XLFont(name="微软雅黑", size=11, bold=True)
            cell.alignment = XLAlign(horizontal="center", vertical="center")
            cell.border = thin_border
            for c in range(1, 6):
                ws.cell(row=total_row, column=c).border = thin_border
            total = sum(item["subtotal"] for item in self.quote_items)
            total_cell = ws.cell(row=total_row, column=6, value=total)
            total_cell.font = XLFont(name="微软雅黑", size=11, bold=True)
            total_cell.alignment = XLAlign(horizontal="center", vertical="center")
            total_cell.border = thin_border
            # 列宽
            ws.column_dimensions["A"].width = 22
            ws.column_dimensions["B"].width = 22
            ws.column_dimensions["C"].width = 22
            ws.column_dimensions["D"].width = 12
            ws.column_dimensions["E"].width = 10
            ws.column_dimensions["F"].width = 12
            wb.save(file_path)
            show_message("成功", f"报价单已保存至：\n{file_path}")
        except Exception as e:
            show_message("导出失败", f"生成Excel出错：\n{e}", "error")


# ==================== 主应用 ====================
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


class PriceAppMain(App):
    def build(self):
        # 窗口大小（PC端调试用，安卓全屏）
        if not ANDROID:
            Window.size = (800, 600)
        return PriceApp()


def main():
    init_db()
    PriceAppMain().run()


if __name__ == "__main__":
    main()
