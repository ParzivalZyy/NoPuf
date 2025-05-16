import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import sqlite3
from datetime import date, timedelta
import threading
import keyboard

class NoPafApp(ttk.Window):  
    def __init__(self):
        super().__init__(themename="superhero")  
        self.title("NoPaf")
        self.geometry("340x480")
        self.configure(bg="#2b3e4f")
        self.conn = sqlite3.connect("NoPaf.db")
        self.fontX = ("Segoe UI", 18)
        self.last_checked_date = date.today().isoformat()
        self.CounterDayWithNotyag = 0

        self.configure_styles()
        self.create_tables()
        self.update_today_data()
        self.bind_pause_key()
        self.show_main_screen()

    def configure_styles(self):
        style = ttk.Style()
        # Пастельный фиолетовый для основной кнопки
        style.configure(
            "TrueNoPaf.TButton",
            font=("Segoe UI", 14, "bold"),
            background="#b39ddb",      # пастельный фиолетовый
            foreground="#22223b",
            borderwidth=0,
            focusthickness=3,
            focuscolor="#a18cd1"
        )
        style.configure(
            "Plus_Info.TButton",
            font=("Segoe UI", 18, "bold"),
            background="#a18cd1",      # ещё один пастельный фиолетовый
            foreground="#22223b",
            borderwidth=0
        )
        style.configure(
            "Stats_back.TButton",
            font=("Segoe UI", 18, "bold"),
            background="#ede7f6",      # светлый пастельный
            foreground="#22223b",
            borderwidth=0
        )
        # Для эффекта наведения
        style.map(
            "TButton",
            background=[("active", "#9575cd")],  # чуть ярче при наведении
        )

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Дата DATE UNIQUE,
                Тяги INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def update_today_data(self):
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Stats (Дата, Тяги) VALUES (?, 0)", (today,))
        self.conn.commit()

    def check_new_day(self):
        current_date = date.today().isoformat()
        if self.last_checked_date != current_date:
            self.last_checked_date = current_date
            self.update_today_data()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_button(self, text, command, style, x, y, width, height):
        ttk.Button(self, text=text, command=command, style=style).place(x=x, y=y, width=width, height=height)

    def show_main_screen(self):
        self.check_new_day()
        self.clear_window()

        self.counter_canvas = tk.Canvas(self, width=220, height=220, highlightthickness=0, bg="#22223c", bd=0, highlightbackground="#22223c")
        self.counter_canvas.place(x=60, y=100)

        self.circle = self.counter_canvas.create_oval(10, 10, 210, 210, fill="#4a4e69", outline="#22223c", width=4)
        self.counter_text = self.counter_canvas.create_text(110, 110, text="", font=("Segoe UI", 48, "bold"), fill="#2F2C2C")

        self.update_counter_color()

        self.create_button("True NoPaf", self.TrueNoPaf, "TrueNoPaf.TButton", 20, 10, 155, 60)
        self.create_button("+1 Тяга", self.add_tyagi, "Plus_Info.TButton", 110, 350, 120, 60)
        self.create_button("Stats", self.show_stats, "Stats_back.TButton", 200, 10, 120, 60)

    def get_tyagi(self, target_date):
        conn = sqlite3.connect("NoPaf.db") 
        cursor = conn.cursor()
        cursor.execute("SELECT Тяги FROM Stats WHERE Дата = ?", (target_date,))
        result = cursor.fetchone()
        conn.close()  
        return result[0] if result else 0

    def add_tyagi(self, threadsafe=False):
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        yesterday_count = self.get_tyagi(yesterday)

        def update_db():
            conn = sqlite3.connect("NoPaf.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO Stats (Дата, Тяги) VALUES (?, 0)", (today,))
            cursor.execute("UPDATE Stats SET Тяги = Тяги + 1 WHERE Дата = ?", (today,))
            conn.commit()
            conn.close()

        if threadsafe:
            def threaded_update():
                update_db()
                self.after(0, self.update_counter_color)
            threading.Thread(target=threaded_update, daemon=True).start()
        else:
            self.check_new_day()
            update_db()
            self.update_counter_color()

        today_count = self.get_tyagi(today)
        if yesterday_count > 0:
            if today_count >= yesterday_count:
                messagebox.showwarning("Ууу какой баран сидит", "Ты уже достиг вчерашнего рекорда, отдыхай")
            elif today_count >= yesterday_count * 0.9:
                messagebox.showwarning("Предупреждение", "Приближаешься к вчерашнему рекорду, стоит прекратить")

    def update_counter_color(self):
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today_count = self.get_tyagi(today)
        yesterday_count = self.get_tyagi(yesterday)

        if yesterday_count == 0:
            new_color = "#b5b6bb"  
        elif today_count < yesterday_count * 0.9:
            new_color = "#66ff66" 
        elif today_count < yesterday_count:
            new_color = "#ffff66"  
        else:
            new_color = "#ff6666"

        self.update_counter_canvas(today_count, new_color)

    def update_counter_canvas(self, value, color):
        self.counter_canvas.itemconfig(self.circle, fill=color)
        self.counter_canvas.itemconfig(self.counter_text, text=str(value))

    def Back(self):
        self.clear_window()
        self.show_main_screen()

    def show_stats(self):
        self.check_new_day()
        self.clear_window()  
        tk.Label(self, text="Статистика", font=("Segoe UI", 22, "bold"), bg="#22223b", fg="#f2e9e4").place(x=0, y=0, width=340, height=60)
    
        stats_frame = tk.Frame(self, bg="#22223b")
        stats_frame.place(x=20, y=70, width=300, height=300)
    
        scrollbar = ttk.Scrollbar(stats_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        tree = ttk.Treeview(stats_frame, columns=("Дата", "Тяги"), show="headings", yscrollcommand=scrollbar.set, style="Treeview")
        tree.heading("Дата", text="Дата")
        tree.heading("Тяги", text="Тяги")
        tree.column("Дата", anchor="center", width=150)
        tree.column("Тяги", anchor="center", width=100)
        tree.pack(fill=tk.BOTH, expand=True)
    
        scrollbar.config(command=tree.yview)
    
        cursor = self.conn.cursor()
        cursor.execute("SELECT Дата, Тяги FROM Stats ORDER BY Дата DESC")
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0], row[1]))

        self.create_button("Назад", self.Back, "Stats_back.TButton", 90, 400, 160, 65)

    def infoTrueNoPaf(self):
        messagebox.showinfo("True NoPaf", "В этом режиме приложения будут автоматически считаться дни без затяжек подряд") 

    def TrueNoPaf(self):
        self.clear_window()
        self.counter_ClearDaylabel = tk.Label(self, text="", font=("Segoe UI", 44, "bold"), bg="#4a4e69", fg="#f2e9e4")
        self.counter_ClearDaylabel.place(x=20, y=40, width=300, height=120)

        ttk.Button(self, text="Назад", command=self.Back, style="Stats_back.TButton").place(x=180, y=200, width=120, height=60)
        ttk.Button(self, text="ЧаВо?", command=self.infoTrueNoPaf, style="Plus_Info.TButton").place(x=40, y=200, width=120, height=60)         
     
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        yesterday_count = self.get_tyagi(yesterday)
        if yesterday_count == 0: 
            self.CounterDayWithNotyag += 1
            self.counter_ClearDaylabel.config(text=str(self.CounterDayWithNotyag), bg="#66ff66")
        else: 
            self.CounterDayWithNotyag = 0
            self.counter_ClearDaylabel.config(text=str(self.CounterDayWithNotyag), bg="#ff6666")

    def bind_pause_key(self):
        def listen():
            keyboard.add_hotkey("pause", lambda: self.add_tyagi(threadsafe=True))
            keyboard.wait()
        threading.Thread(target=listen, daemon=True).start()

if __name__ == "__main__":
    app = NoPafApp()
    app.mainloop()