# -*- coding: utf-8 -*-
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

import csv
import datetime
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.utils import platform

# ---- Android 专用导入（桌面端不执行） ----
if platform == "android":
    from android.permissions import request_permissions, check_permission, Permission
    from android.storage import primary_external_storage_path

# ---- 中文字体：优先用项目目录字体，否则用 Windows 系统字体 ----
def load_cjk_font():
    candidates = [
        "NotoSansSC-Regular.ttf",                # 项目目录（安卓打包时用）
        r"C:\Windows\Fonts\simhei.ttf",          # 黑体，Windows 自带
        r"C:\Windows\Fonts\msyh.ttc",            # 微软雅黑
    ]
    for path in candidates:
        if os.path.exists(path):
            LabelBase.register(name="CJK", fn_regular=path)
            return "CJK"
    return "Roboto"

FONT = load_cjk_font()

WEEKS = ["第一周", "第二周", "第三周", "第四周", "第五周"]
RESULTS = ["—", "√", "×"]

# (分组, 检查内容/部位, 技术参数, 是否温度项)
TEMPLATE_A = [
    ("室内插座", "外观", "安装牢固，面板紧固", False),
    ("室内插座", "功能", "插座与插头连接紧密，无缝隙，轻微外力不掉落", False),
    ("室内插座", "插口颜色", "插口无发黑，无高温变形，无异味", False),
    ("室内插座", "外露线路", "接头牢固，绝缘良好", False),
    ("室内插座", "异响", "插座内无异响", False),
    ("室内插座", "温度", "插座、插头处无异常高温（测温枪测试）", True),
    ("开关照明", "开关外观", "安装牢固，面板紧固", False),
    ("开关照明", "开关功能", "按键开关顺滑，控制正常，无异味", False),
    ("开关照明", "灯具外观", "安装牢固，无破损，灯架灯管接触紧密", False),
    ("开关照明", "外露线路", "接头牢固，绝缘良好", False),
    ("开关照明", "灯具功能", "正常点亮，无闪烁、点亮滞后、异响", False),
    ("配电盘、箱", "低压断路器外观", "无缺损，端子无烧黑、变色", False),
    ("配电盘、箱", "低压断路器标识", "清晰、准确、无缺失", False),
    ("配电盘、箱", "断路器/漏保异常", "无异响、异味", False),
    ("配电盘、箱", "低压配电盘", "干净无油污，柜门开闭正常，接地牢固，有防触电标识，无异味", False),
    ("配电盘、箱", "裸露线路", "接头牢固、绝缘良好，与开关断路器接点牢固，裸露线头不超过5mm", False),
    ("配电盘、箱", "防触电标识", "粘贴牢固，标识清晰", False),
]

TEMPLATE_B = [
    ("低压配电柜", "低压断路器外观", "无缺损，端子无烧黑、变色", False),
    ("低压配电柜", "低压断路器标识", "清晰、准确、无缺失", False),
    ("低压配电柜", "柜体整体", "干净无油污，柜门关闭、开启正常，接地线牢固，有防触电标识", False),
    ("低压配电柜", "断路器/漏保异常", "无异响、异味", False),
    ("低压配电柜", "裸露线路", "接头牢固、绝缘良好，与开关断路器接点牢固，裸露线头不超过5mm", False),
    ("低压配电柜", "配电室房屋墙面", "无漏水、无墙皮脱落", False),
    ("低压配电柜", "防触电标识", "粘贴牢固，标识清晰", False),
]

TEMPLATES = {
    "A": ("室内插座、开关、照明、配电盘、配电箱检查", TEMPLATE_A),
    "B": ("低压配电柜检查", TEMPLATE_B),
}


def make_label(text, size_hint_x=1, bold=False, size="14sp", **kw):
    lbl = Label(text=text, font_name=FONT, font_size=size,
                size_hint_x=size_hint_x, bold=bold,
                valign="middle", padding=(6, 2), **kw)
    lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    return lbl


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation="vertical", padding=12, spacing=10)

        root.add_widget(make_label("电气设备巡检记录系统", bold=True, size="20sp"))

        form = BoxLayout(orientation="vertical", size_hint_y=0.45, spacing=6)
        row1 = BoxLayout(spacing=6)
        row1.add_widget(make_label("设备编号：", size_hint_x=0.35))
        self.eq_id = TextInput(hint_text="如：PD-001", multiline=False, font_name=FONT)
        row1.add_widget(self.eq_id)
        form.add_widget(row1)

        now = datetime.datetime.now()
        row2 = BoxLayout(spacing=6)
        row2.add_widget(make_label("巡检年月：", size_hint_x=0.35))
        self.ym = TextInput(text=now.strftime("%Y-%m"), multiline=False, font_name=FONT)
        row2.add_widget(self.ym)
        form.add_widget(row2)

        root.add_widget(form)

        root.add_widget(make_label("请选择检查标准：", size="15sp"))
        for key, (title, _) in TEMPLATES.items():
            btn = Button(text=title, font_name=FONT, size_hint_y=None, height="52dp")
            btn.bind(on_release=lambda inst, k=key: self.start_check(k))
            root.add_widget(btn)

        self.add_widget(root)

    def start_check(self, key):
        title, items = TEMPLATES[key]
        sm = self.manager
        if "check" in sm.screen_names:
            sm.remove_widget(sm.get_screen("check"))
        sm.add_widget(CheckScreen(name="check", title=title, items=items,
                                  eq_id=self.eq_id.text.strip(), ym=self.ym.text.strip()))
        sm.current = "check"


class CheckScreen(Screen):
    def __init__(self, title, items, eq_id, ym, **kw):
        super().__init__(**kw)
        self.eq_id, self.ym = eq_id, ym
        self.rows = {}   # (group, part) -> {"spinner":..., "temp":...}

        root = BoxLayout(orientation="vertical", padding=8, spacing=6)

        # 顶部：标题 + 周选择
        top = BoxLayout(size_hint_y=None, height="48dp", spacing=6)
        back = Button(text="返回", font_name=FONT, size_hint_x=0.2)
        back.bind(on_release=lambda i: setattr(self.manager, "current", "home"))
        top.add_widget(back)
        top.add_widget(make_label(title, size_hint_x=0.55, bold=True, size="15sp"))
        self.week_sp = Spinner(text=WEEKS[0], values=WEEKS, font_name=FONT, size_hint_x=0.25)
        top.add_widget(self.week_sp)
        root.add_widget(top)

        # 检查项列表
        sv = ScrollView()
        lst = BoxLayout(orientation="vertical", size_hint_y=None, spacing=2)
        lst.bind(minimum_height=lst.setter("height"))
        cur_group = None
        for group, part, param, is_temp in items:
            if group != cur_group:
                cur_group = group
                lst.add_widget(make_label("■ " + group, bold=True, size="16sp",
                                          size_hint_y=None, height="34dp"))
            row = BoxLayout(size_hint_y=None, height="58dp", spacing=4)
            info = make_label("%s｜%s\n%s" % (part, param, ""), size_hint_x=0.52, size="12sp")
            row.add_widget(info)
            sp = Spinner(text="—", values=RESULTS, font_name=FONT, size_hint_x=0.2)
            row.add_widget(sp)
            if is_temp:
                ti = TextInput(hint_text="℃", multiline=False, font_name=FONT, size_hint_x=0.28)
                row.add_widget(ti)
            else:
                ti = None
                row.add_widget(make_label("", size_hint_x=0.28))
            self.rows[(group, part)] = {"spinner": sp, "temp": ti}
            lst.add_widget(row)
        sv.add_widget(lst)
        root.add_widget(sv)

        # 底部：异常 + 签字
        bottom = BoxLayout(orientation="vertical", size_hint_y=None, height="150dp", spacing=4)
        r1 = BoxLayout(spacing=6)
        r1.add_widget(make_label("异常情况：", size_hint_x=0.3))
        self.abnormal = TextInput(hint_text="无异常填“无”；有异常立即上报并填写记录",
                                  multiline=True, font_name=FONT)
        r1.add_widget(self.abnormal)
        bottom.add_widget(r1)
        r2 = BoxLayout(spacing=6)
        r2.add_widget(make_label("巡检人(时间)：", size_hint_x=0.3))
        self.inspector = TextInput(hint_text="张三 08:30", multiline=False, font_name=FONT)
        r2.add_widget(self.inspector)
        bottom.add_widget(r2)
        r3 = BoxLayout(spacing=6)
        r3.add_widget(make_label("检查人(时间)：", size_hint_x=0.3))
        self.checker = TextInput(hint_text="李四 17:00", multiline=False, font_name=FONT)
        r3.add_widget(self.checker)
        bottom.add_widget(r3)

        save = Button(text="保存本周记录", font_name=FONT, size_hint_y=None, height="48dp",
                      background_color=(0.2, 0.6, 0.9, 1))
        save.bind(on_release=self.save)
        bottom.add_widget(save)
        root.add_widget(bottom)

        self.add_widget(root)

    def _get_save_paths(self, fname):
        """返回可写入的目标路径列表"""
        paths = []
        app = App.get_running_app()

        # 1) 应用私有目录（无需权限，始终可写）
        paths.append(os.path.join(app.user_data_dir, fname))

        # 2) Android 外部存储（需要权限）
        if platform == "android":
            try:
                if check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                    base = primary_external_storage_path()
                    ext_dir = os.path.join(base, "巡检记录")
                    os.makedirs(ext_dir, exist_ok=True)
                    paths.append(os.path.join(ext_dir, fname))
            except Exception as e:
                print("外部存储路径获取失败:", e)

        return paths

    def save(self, *_):
        week = self.week_sp.text
        fname = "巡检记录_%s_%s_%s.csv" % (self.eq_id or "设备", self.ym, week)
        header = ["设备编号", "年月", "周次", "分组", "检查部位", "检查结果",
                  "温度(℃)", "异常情况", "巡检人(时间)", "检查人(时间)", "保存时间"]

        paths = self._get_save_paths(fname)

        saved = []
        errors = []
        for path in paths:
            try:
                with open(path, "w", newline="", encoding="utf-8-sig") as f:
                    w = csv.writer(f)
                    w.writerow(header)
                    for (group, part), widgets in self.rows.items():
                        temp = widgets["temp"].text.strip() if widgets["temp"] else ""
                        w.writerow([self.eq_id, self.ym, week, group, part,
                                    widgets["spinner"].text, temp,
                                    self.abnormal.text.strip(),
                                    self.inspector.text.strip(),
                                    self.checker.text.strip(),
                                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                saved.append(path)
            except Exception as e:
                errors.append("%s\n  → %s" % (path, e))

        if saved:
            msg = "已保存到：\n" + "\n".join(saved)
            if errors:
                msg += "\n\n部分路径失败：\n" + "\n".join(errors)
            self.popup("保存成功", msg)
        else:
            self.popup("保存失败", "没有可写入的目录\n\n" + "\n".join(errors))

    @staticmethod
    def popup(title, msg):
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(make_label(msg, size="13sp"))
        btn = Button(text="确定", font_name=FONT, size_hint_y=None, height="44dp")
        box.add_widget(btn)
        p = Popup(title=title, content=box, size_hint=(0.85, 0.6), auto_dismiss=False)
        btn.bind(on_release=p.dismiss)
        p.open()


class XunJianApp(App):
    def build(self):
        # Android 平台：先请求存储权限
        if platform == "android":
            self._request_android_permissions()

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        return sm

    def _request_android_permissions(self):
        """在应用启动时请求存储权限（异步，不阻塞 UI）"""
        try:
            permissions = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ]
            need = [p for p in permissions if not check_permission(p)]
            if need:
                request_permissions(need, self._on_permissions_result)
        except Exception as e:
            print("权限请求失败:", e)

    def _on_permissions_result(self, permissions, results):
        for p, r in zip(permissions, results):
            print("权限 %s -> %s" % (p, "已授予" if r else "被拒绝"))


if __name__ == "__main__":
    XunJianApp().run()