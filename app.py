"""Local meal, training, and wellness journal. Standard library only."""

from __future__ import annotations

import csv
import json
import os
import sys
import tkinter as tk
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_NAME = "日常 · 饮食与训练"
DATA_FILE = Path(__file__).with_name("data.json")
BG = "#f5f4f0"
CARD = "#ffffff"
INK = "#20231f"
MUTED = "#858981"
GREEN = "#52745c"
PALE_GREEN = "#e8eee6"
LINE = "#e9e9e4"


def today() -> str:
    return date.today().isoformat()


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "settings": {"calories": 2000, "protein": 140},
        "meals": [], "training": [], "wellness": []
    }


class JournalApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.data = load_data()
        self.selected_date = tk.StringVar(value=today())
        self.root.title(APP_NAME)
        self.root.geometry("1100x780")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)
        self._style()
        self._build()
        self.refresh()

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=INK, rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=BG, foreground=MUTED,
                        borderwidth=0, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", PALE_GREEN)],
                  foreground=[("selected", INK)])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10), background=BG,
                        foreground=MUTED, font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", CARD)],
                  foreground=[("selected", INK)])

    def save(self):
        DATA_FILE.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=34, pady=(24, 20))

        top = tk.Frame(outer, bg=BG)
        top.pack(fill="x", pady=(0, 22))
        left = tk.Frame(top, bg=BG)
        left.pack(side="left")
        tk.Label(left, text="日常", bg=BG, fg=INK, font=("Segoe UI", 25, "bold")).pack(anchor="w")
        tk.Label(left, text="饮食 · 训练 · 状态", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(1, 0))
        date_box = tk.Frame(top, bg=BG)
        date_box.pack(side="right", pady=8)
        tk.Label(date_box, text="查看日期", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(0, 8))
        date_entry = tk.Entry(date_box, textvariable=self.selected_date, width=12,
                              relief="flat", bg=CARD, fg=INK, insertbackground=INK,
                              font=("Segoe UI", 10))
        date_entry.pack(side="left", ipady=8, ipadx=7)
        date_entry.bind("<Return>", lambda _e: self.refresh())
        self._button(date_box, "今天", self.go_today, subtle=True).pack(side="left", padx=(7, 0))

        self.cards = tk.Frame(outer, bg=BG)
        self.cards.pack(fill="x", pady=(0, 20))

        self.tabs = ttk.Notebook(outer)
        self.tabs.pack(fill="both", expand=True)
        self.meals_tab = tk.Frame(self.tabs, bg=CARD)
        self.training_tab = tk.Frame(self.tabs, bg=CARD)
        self.trends_tab = tk.Frame(self.tabs, bg=CARD)
        self.tabs.add(self.meals_tab, text="饮食")
        self.tabs.add(self.training_tab, text="训练")
        self.tabs.add(self.trends_tab, text="趋势与设置")
        self._build_meals()
        self._build_training()
        self._build_trends()

        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill="x", pady=(12, 0))
        tk.Label(footer, text="估算值供个人记录参考；照片本身不能准确判断食物重量或营养。",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        self._button(footer, "导出 CSV", self.export_csv, subtle=True).pack(side="right")

    def _card(self, parent, title, value, suffix, note, accent=False):
        box = tk.Frame(parent, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        tk.Label(box, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=(14, 5))
        row = tk.Frame(box, bg=CARD)
        row.pack(anchor="w", padx=17)
        tk.Label(row, text=value, bg=CARD, fg=GREEN if accent else INK,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(row, text=suffix, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(5, 0), pady=(9, 0))
        tk.Label(box, text=note, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=(1, 14))
        return box

    def _button(self, parent, text, command, subtle=False):
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                         bg=BG if subtle else GREEN, fg=INK if subtle else "white",
                         activebackground=PALE_GREEN if subtle else "#44674f",
                         activeforeground=INK if subtle else "white",
                         cursor="hand2", padx=13, pady=8, font=("Segoe UI", 9, "bold"))

    def _section_header(self, parent, title, action, command):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=22, pady=(20, 12))
        tk.Label(row, text=title, bg=CARD, fg=INK, font=("Segoe UI", 14, "bold")).pack(side="left")
        self._button(row, action, command).pack(side="right")

    def _tree(self, parent, columns, headings, widths):
        wrap = tk.Frame(parent, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        tree = ttk.Treeview(wrap, columns=columns, show="headings", selectmode="browse")
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor="w")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _build_meals(self):
        self._section_header(self.meals_tab, "今天吃了什么", "＋ 记录一餐", self.add_meal)
        self.meal_tree = self._tree(self.meals_tab,
                                    ("time", "meal", "foods", "kcal", "protein", "photo"),
                                    ("时间", "餐次", "食物与份量", "热量估算", "蛋白质", "照片"),
                                    (90, 90, 380, 110, 100, 220))
        bar = tk.Frame(self.meals_tab, bg=CARD)
        bar.pack(fill="x", padx=22, pady=(0, 18))
        self._button(bar, "删除选中记录", self.delete_meal, subtle=True).pack(side="left")
        tk.Label(bar, text="份量尽量手动填写；营养数字可随时修正。", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=12)

    def _build_training(self):
        self._section_header(self.training_tab, "训练与活动", "＋ 记录训练", self.add_training)
        self.training_tree = self._tree(self.training_tab,
                                        ("time", "type", "details", "duration", "weight"),
                                        ("时间", "项目", "动作 / 组数 / 次数", "时长", "体重"),
                                        (100, 130, 420, 110, 100))
        bar = tk.Frame(self.training_tab, bg=CARD)
        bar.pack(fill="x", padx=22, pady=(0, 18))
        self._button(bar, "删除选中记录", self.delete_training, subtle=True).pack(side="left")
        tk.Label(bar, text="记录重量与次数，方便下次循序渐进。", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=12)
        self._button(bar, "记录体重 / 睡眠", self.add_wellness, subtle=True).pack(side="right")

    def _build_trends(self):
        head = tk.Frame(self.trends_tab, bg=CARD)
        head.pack(fill="x", padx=22, pady=(20, 10))
        tk.Label(head, text="近 7 天", bg=CARD, fg=INK, font=("Segoe UI", 14, "bold")).pack(side="left")
        self._button(head, "编辑每日目标", self.edit_goals, subtle=True).pack(side="right")
        self.trend_area = tk.Frame(self.trends_tab, bg=CARD)
        self.trend_area.pack(fill="both", expand=True, padx=22, pady=(0, 20))
        self.trend_summary = tk.Label(self.trend_area, text="", justify="left", anchor="nw",
                                      bg=CARD, fg=INK, font=("Segoe UI", 11), padx=15, pady=14)
        self.trend_summary.pack(fill="x", pady=(4, 15))
        settings = tk.Frame(self.trend_area, bg=BG)
        settings.pack(fill="x", pady=6)
        tk.Label(settings, text="数据存放在本机同目录的 data.json 中。", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=12, pady=10)
        self._button(settings, "打开数据文件夹", self.open_data_folder, subtle=True).pack(side="right", padx=8, pady=5)

    def go_today(self):
        self.selected_date.set(today())
        self.refresh()

    def rows(self, key):
        return [x for x in self.data.get(key, []) if x.get("date") == self.selected_date.get()]

    def refresh(self):
        try:
            datetime.strptime(self.selected_date.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("日期格式", "请输入 YYYY-MM-DD 格式的日期。")
            return
        meals = self.rows("meals")
        kcal = sum(float(x.get("kcal") or 0) for x in meals)
        protein = sum(float(x.get("protein") or 0) for x in meals)
        workouts = self.rows("training")
        wellness = next((x for x in self.rows("wellness")), {})
        goals = self.data["settings"]
        for child in self.cards.winfo_children():
            child.destroy()
        summaries = [
            ("摄入热量", f"{kcal:g}", f"/ {goals['calories']} kcal", f"{len(meals)} 餐记录", False),
            ("蛋白质", f"{protein:g}", f"/ {goals['protein']} g", f"还差 {max(0, float(goals['protein'])-protein):g} g" if protein < float(goals['protein']) else "已达到今日目标", True),
            ("训练", str(len(workouts)), "项活动", "以实际训练记录为准", False),
            ("体重 / 睡眠", wellness.get("weight", "—"), "kg", f"睡眠 {wellness.get('sleep', '—')} 小时", False),
        ]
        for i, item in enumerate(summaries):
            self._card(self.cards, *item).grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            self.cards.grid_columnconfigure(i, weight=1, uniform="cards")
        self.meal_tree.delete(*self.meal_tree.get_children())
        for i, x in enumerate(meals):
            self.meal_tree.insert("", "end", iid=str(i), values=(x.get("time", ""), x.get("meal", ""),
                x.get("foods", ""), x.get("kcal", "—"), x.get("protein", "—"),
                Path(x["photo"]).name if x.get("photo") else "—"))
        self.training_tree.delete(*self.training_tree.get_children())
        for i, x in enumerate(workouts):
            self.training_tree.insert("", "end", iid=str(i), values=(x.get("time", ""), x.get("type", ""),
                x.get("details", ""), x.get("duration", "—"), x.get("weight", "—")))
        self._refresh_trends()

    def _refresh_trends(self):
        end = date.fromisoformat(self.selected_date.get())
        lines = []
        for offset in range(6, -1, -1):
            day = (end - timedelta(days=offset)).isoformat()
            meals = [x for x in self.data["meals"] if x.get("date") == day]
            kcal = sum(float(x.get("kcal") or 0) for x in meals)
            protein = sum(float(x.get("protein") or 0) for x in meals)
            wellness = next((x for x in self.data["wellness"] if x.get("date") == day), {})
            marker = "  ←" if day == self.selected_date.get() else ""
            lines.append(f"{day}   热量 {kcal:g} kcal     蛋白质 {protein:g} g     体重 {wellness.get('weight', '—')} kg{marker}")
        self.trend_summary.config(text="\n\n".join(lines))

    def _dialog(self, title, fields, initial=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=CARD)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        values = {}
        body = tk.Frame(win, bg=CARD)
        body.pack(padx=22, pady=(20, 8), fill="both")
        for i, (key, label, kind) in enumerate(fields):
            tk.Label(body, text=label, bg=CARD, fg=INK, font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=7, padx=(0, 12))
            if kind == "meal":
                widget = ttk.Combobox(body, values=["早餐", "午餐", "晚餐", "加餐"], state="readonly", width=31)
                widget.set((initial or {}).get(key, "午餐"))
            elif kind == "file":
                line = tk.Frame(body, bg=CARD)
                line.grid(row=i, column=1, sticky="ew", pady=5)
                var = tk.StringVar(value=(initial or {}).get(key, ""))
                widget = tk.Entry(line, textvariable=var, width=28, relief="solid", bd=1, font=("Segoe UI", 9))
                widget.pack(side="left", ipady=5)
                def choose(v=var):
                    path = filedialog.askopenfilename(title="选择餐食照片", filetypes=[("图片", "*.png *.jpg *.jpeg *.webp *.bmp"), ("所有文件", "*.*")])
                    if path:
                        v.set(path)
                tk.Button(line, text="浏览…", command=choose, relief="flat", bg=BG, fg=INK).pack(side="left", padx=6)
                values[key] = var
                continue
            else:
                widget = tk.Entry(body, width=34, relief="solid", bd=1, font=("Segoe UI", 9))
                widget.insert(0, str((initial or {}).get(key, "")))
            widget.grid(row=i, column=1, sticky="ew", pady=5, ipady=5)
            values[key] = widget
        buttons = tk.Frame(win, bg=CARD)
        buttons.pack(fill="x", padx=22, pady=(10, 20))
        result = {}
        def submit():
            for key, _, _ in fields:
                result[key] = values[key].get().strip()
            win.destroy()
        self._button(buttons, "取消", win.destroy, subtle=True).pack(side="right", padx=(8, 0))
        self._button(buttons, "保存记录", submit).pack(side="right")
        win.bind("<Return>", lambda _e: submit())
        win.wait_window()
        return result or None

    def _number(self, value, label):
        if value == "":
            return ""
        try:
            number = float(value)
            if number < 0:
                raise ValueError
            return number
        except ValueError:
            raise ValueError(f"{label}请填写不小于 0 的数字。")

    def add_meal(self):
        fields = [("meal", "餐次", "meal"), ("foods", "食物与份量", "text"),
                  ("kcal", "热量估算（kcal）", "text"), ("protein", "蛋白质（g）", "text"),
                  ("photo", "照片（可选）", "file"), ("note", "备注（可选）", "text")]
        result = self._dialog("记录一餐", fields)
        if not result:
            return
        if not result["foods"]:
            messagebox.showinfo("还差一点", "请填写食物名称和大致份量。")
            return
        try:
            result["kcal"] = self._number(result["kcal"], "热量")
            result["protein"] = self._number(result["protein"], "蛋白质")
        except ValueError as e:
            messagebox.showerror("检查数字", str(e)); return
        result.update(date=self.selected_date.get(), time=datetime.now().strftime("%H:%M"))
        self.data["meals"].append(result); self.save(); self.refresh()

    def delete_meal(self):
        selected = self.meal_tree.selection()
        if not selected:
            return
        item = self.rows("meals")[int(selected[0])]
        self.data["meals"].remove(item); self.save(); self.refresh()

    def add_training(self):
        fields = [("type", "项目", "text"), ("details", "动作 / 组数 / 次数", "text"),
                  ("duration", "时长（分钟，可选）", "text"), ("weight", "体重（kg，可选）", "text"),
                  ("note", "备注（可选）", "text")]
        result = self._dialog("记录训练", fields)
        if not result or not result["type"]:
            return
        try:
            result["duration"] = self._number(result["duration"], "时长")
            result["weight"] = self._number(result["weight"], "体重")
        except ValueError as e:
            messagebox.showerror("检查数字", str(e)); return
        result.update(date=self.selected_date.get(), time=datetime.now().strftime("%H:%M"))
        self.data["training"].append(result); self.save(); self.refresh()

    def delete_training(self):
        selected = self.training_tree.selection()
        if not selected:
            return
        item = self.rows("training")[int(selected[0])]
        self.data["training"].remove(item); self.save(); self.refresh()

    def add_wellness(self):
        current = next((x for x in self.rows("wellness")), {})
        result = self._dialog("每日状态", [("weight", "体重（kg，可选）", "text"),
                                            ("sleep", "睡眠（小时，可选）", "text"),
                                            ("note", "状态备注（可选）", "text")], current)
        if not result:
            return
        try:
            result["weight"] = self._number(result["weight"], "体重")
            result["sleep"] = self._number(result["sleep"], "睡眠")
        except ValueError as e:
            messagebox.showerror("检查数字", str(e)); return
        existing = next((x for x in self.rows("wellness")), None)
        result["date"] = self.selected_date.get()
        if existing:
            self.data["wellness"].remove(existing)
        self.data["wellness"].append(result)
        self.save(); self.refresh()

    def edit_goals(self):
        result = self._dialog("每日目标", [("calories", "热量目标（kcal）", "text"),
                                           ("protein", "蛋白质目标（g）", "text")], self.data["settings"])
        if not result:
            return
        try:
            calories = self._number(result["calories"], "热量")
            protein = self._number(result["protein"], "蛋白质")
            if not calories or not protein:
                raise ValueError("目标请填写大于 0 的数字。")
        except ValueError as e:
            messagebox.showerror("检查目标", str(e)); return
        self.data["settings"] = {"calories": calories, "protein": protein}
        self.save(); self.refresh()

    def export_csv(self):
        path = filedialog.asksaveasfilename(title="导出记录", defaultextension=".csv",
                    initialfile="饮食训练记录.csv", filetypes=[("CSV 文件", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["类型", "日期", "时间", "餐次/项目", "内容", "热量 kcal", "蛋白质 g", "备注"])
            for x in self.data["meals"]:
                writer.writerow(["饮食", x.get("date"), x.get("time"), x.get("meal"), x.get("foods"), x.get("kcal"), x.get("protein"), x.get("note")])
            for x in self.data["training"]:
                writer.writerow(["训练", x.get("date"), x.get("time"), x.get("type"), x.get("details"), "", "", x.get("note")])
            for x in self.data["wellness"]:
                writer.writerow(["状态", x.get("date"), "", "体重/睡眠", "", "", "", f"体重 {x.get('weight')} kg；睡眠 {x.get('sleep')} 小时"])
        messagebox.showinfo("导出完成", f"记录已导出到：\n{path}")

    def open_data_folder(self):
        os.startfile(str(DATA_FILE.parent))


def main():
    root = tk.Tk()
    JournalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
