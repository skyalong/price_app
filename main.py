# minimal.py
from kivy.app import App
from kivy.uix.label import Label



class MinimalApp(App):
    def build(self):
        return Label(text="Hello World!")


###################################################################################################
class QuoteScreen(Screen):
    cart_items = []
    q_table = None
    cart_table = None

    def on_enter(self):
        self.q_search()
        self.refresh_cart()

    def q_search(self):
        key = self.ids.q_search.text.strip()
        self.ids.q_table_box.clear_widgets()

        try:
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
                    ("价格", dp(80))
                ],
                row_data=res
            )
            self.ids.q_table_box.add_widget(table)
            self.q_table = table

        except Exception as e:
            Snackbar(text=f"查询失败: {str(e)}", duration=2).open()

    def get_selected_quote_row(self):
        if self.q_table is None:
            return None
        if hasattr(self.q_table, 'current_row') and self.q_table.current_row:
            return self.q_table.current_row
        return None

    def add_cart(self):
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

    def refresh_cart(self):
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
            row_data=rows
        )
        self.ids.cart_box.add_widget(table)
        self.cart_table = table
        self.ids.total_text.text = f"总金额：{total:.2f} 元"

    def get_selected_cart_row(self):
        if self.cart_table is None:
            return None
        if hasattr(self.cart_table, 'current_row') and self.cart_table.current_row:
            return self.cart_table.current_row
        return None

    def del_cart(self):
        row = self.get_selected_cart_row()
        if not row:
            Snackbar(text="请选择要删除的项目！", duration=2).open()
            return

        for i, item in enumerate(self.cart_items):
            if item["project_name"] == row[0] and item["model_spec"] == row[1]:
                del self.cart_items[i]
                break

        self.refresh_cart()

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
        if not HAS_OPENPYXL:
            Snackbar(text="请安装 openpyxl 模块", duration=3).open()
            return

        if not self.cart_items:
            Snackbar(text="报价单为空！", duration=2).open()
            return

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

        filename = f"报价单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(save_dir, filename)

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "报价单"

            ws.merge_cells("A1:F1")
            ws["A1"] = "检校业务报价单"
            ws["A1"].font = Font(name="微软雅黑", size=16, bold=True)
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 35

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

            ws.column_dimensions["A"].width = 22
            ws.column_dimensions["B"].width = 22
            ws.column_dimensions["C"].width = 22
            ws.column_dimensions["D"].width = 12
            ws.column_dimensions["E"].width = 10
            ws.column_dimensions["F"].width = 12

            wb.save(file_path)
            Snackbar(text=f"报价单已保存到:\n{file_path}", duration=4).open()

        except Exception as e:
            Snackbar(text=f"导出失败: {str(e)}", duration=3).open()
##############################################################################################
if __name__ == "__main__":
    QuoteScreen().run()# MinimalApp().run()