import sqlite3
import threading
from datetime import date, timedelta, datetime

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import keyboard
from PIL import Image, ImageTk

class NoPafApp(ttk.Window):
    BG_COLOR = "#2b3e4f"
    STATS_BG_COLOR = "#22223b"
    
    IMAGES = {
        "true_nopaf": "pictures/True NoPaf.png",
        "plus": "pictures/1Plus.png",
        "stats": "pictures/Stats.png",
        "back": "pictures/Back.png",
        "what": "pictures/What.png",
        "circle_white": "pictures/circle_white.png",
        "circle_green": "pictures/circle_green.png",
        "circle_yellow": "pictures/circle_yellow.png", 
        "circle_red": "pictures/circle_red.png"
    }
    
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("NoPaf")
        self.geometry("340x480")
        self.configure(bg=self.BG_COLOR)
        self.conn = sqlite3.connect("NoPaf.db")
        self.last_checked_date = date.today().isoformat()
        self.CounterDayWithNotyag = 0


        self.img_true_nopaf = self.load_image("true_nopaf", (110, 70))
        self.img_plus = self.load_image("plus", (130, 70))
        self.img_stats = self.load_image("stats", (110, 70))
        self.img_back = self.load_image("back", (135, 88))
        self.img_what = self.load_image("what", (135, 85))
        
        self.circle_white = ImageTk.PhotoImage(Image.open(self.IMAGES["circle_white"]).resize((200, 200), Image.LANCZOS))
        self.circle_green = ImageTk.PhotoImage(Image.open(self.IMAGES["circle_green"]).resize((200, 200), Image.LANCZOS))
        self.circle_yellow = ImageTk.PhotoImage(Image.open(self.IMAGES["circle_yellow"]).resize((200, 200), Image.LANCZOS))
        self.circle_red = ImageTk.PhotoImage(Image.open(self.IMAGES["circle_red"]).resize((200, 200), Image.LANCZOS))

        self.create_tables()
        self.update_today_data()
        self.bind_pause_key()
        self.show_main_screen()

    def load_image(self, image_name, size):
        img = Image.open(self.IMAGES[image_name]).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    
    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS Stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Дата DATE UNIQUE,
                    Тяги INTEGER DEFAULT 0
                )
            ''')

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

    def show_main_screen(self):
        self.check_new_day()
        self.clear_window()
        
        self.circle_label = tk.Label(self, image=self.circle_white, bg=self.BG_COLOR, bd=0)
        self.circle_label.place(x=70, y=90, width=200, height=200)  
        
        self.counter_text_label = tk.Label(self, text="", font=("Segoe UI", 34, "bold"), fg="#2F2C2C", bg=self.BG_COLOR)
        self.counter_text_label.place(x=170, y=190, anchor="center", width=80, height=50)

        self.recomend_label = tk.Label(self, text="", font=("Calibri", 12, "bold"), fg="#4c3086", bg="#e3d5f8")
        self.recomend_label.place(x=170, y=325, anchor="center")

        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today_count = self.get_tyagi(today)
        yesterday_count = self.get_tyagi(yesterday)

        self.update_counter_color()
        if yesterday_count > 0 and today_count < yesterday_count - 4:
            interval_text = self.calculate_interval(today_count, yesterday_count)
            self.recomend_label.config(text=interval_text, fg="#4c3086", bg="#e3d5f8", font=("Calibri", 12, "bold"))
        else:
            self.recomend_label.config(bg=self.BG_COLOR)

        tk.Button(self, image=self.img_true_nopaf, command=self.TrueNoPaf, borderwidth=0, bg=self.BG_COLOR, activebackground=self.BG_COLOR).place(x=20, y=10, width=105, height=70)
        tk.Button(self, image=self.img_stats, command=self.show_stats, borderwidth=0, bg=self.BG_COLOR, activebackground=self.BG_COLOR).place(x=210, y=10, width=105, height=70)  
        tk.Button(self, image=self.img_plus, command=self.add_tyagi, borderwidth=0, bg=self.BG_COLOR, activebackground=self.BG_COLOR).place(x=110, y=360, width=120, height=60)

    def get_tyagi(self, target_date):
        with sqlite3.connect("NoPaf.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Тяги FROM Stats WHERE Дата = ?", (target_date,))
            result = cursor.fetchone()
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

            today_count = self.get_tyagi(today)
            if yesterday_count > 0 and today_count < yesterday_count - 4:
                interval_text = self.calculate_interval(today_count, yesterday_count)
                if hasattr(self, 'interval_label'):
                    self.recomend_label.config(text=interval_text, fg="#4c3086", bg="#e3d5f8")

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

        circle_img, counter_bg = self.get_circle_properties(today_count, yesterday_count)

        self.circle_label.config(image=circle_img)
        self.circle_label.image = circle_img
        self.counter_text_label.config(text=str(today_count), bg=counter_bg, fg="#2F2C2C")
        
        if yesterday_count > 0 and today_count < yesterday_count - 4:
            interval_text = self.calculate_interval(today_count, yesterday_count)
            self.recomend_label.config(text=interval_text, fg="#4c3086", bg="#e3d5f8", font=("Calibri", 12, "bold"))

    def get_circle_properties(self, today_count, yesterday_count):
        if yesterday_count is None or yesterday_count == 0:
            return self.circle_white, "#ffffff"
        elif today_count < yesterday_count - 4:
            return self.circle_green, "#66ff66"
        elif today_count < yesterday_count:
            return self.circle_yellow, "#ffff66"
        else:
            return self.circle_red, "#ff6666"


    def calculate_interval(self, today_count, yesterday_count):
        if yesterday_count is None or yesterday_count == 0:
            return ""
            
        target_puffs = yesterday_count - 4
        if today_count >= target_puffs:
            return ""
        
        remaining_puffs = target_puffs - today_count
        
        current_time = datetime.now()
        end_of_day = current_time.replace(hour=23, minute=59, second=59)
        time_diff = end_of_day - current_time
        
        total_remaining_minutes = (time_diff.seconds // 3600* 60) + (time_diff.seconds % 3600) // 60
        
        if remaining_puffs > 0 and total_remaining_minutes > 0:
            minutes_per_puff = total_remaining_minutes / (remaining_puffs + 1)
            hours = int(minutes_per_puff // 60)
            minutes = int(minutes_per_puff % 60)
            self.remaining_seconds = (hours * 3600) + (minutes * 60)
            return f"Рекомендуемый интервал - {hours}ч {minutes}мин"
        return ""

    def Back(self):
        self.clear_window()
        self.show_main_screen()

    def show_stats(self):
        self.check_new_day()
        self.clear_window()  
        tk.Label(self, text="Статистика", font=("Segoe UI", 22, "bold"), bg=self.STATS_BG_COLOR, fg="#f2e9e4").place(x=0, y=0, width=340, height=60)
        tk.Button(self, image=self.img_back, command=self.Back, borderwidth=0, bg=self.STATS_BG_COLOR, activebackground=self.STATS_BG_COLOR).place(x=120, y=400, width=100, height=60)

        stats_frame = tk.Frame(self, bg=self.STATS_BG_COLOR)
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


    def infoTrueNoPaf(self):
        messagebox.showinfo("True NoPaf", "В этом режиме приложения будут автоматически считаться дни без затяжек подряд") 

    def TrueNoPaf(self):
        self.clear_window()
        
        self.true_nopaf_circle = tk.Label(self, image=self.circle_green, bg=self.BG_COLOR, bd=0)
        self.true_nopaf_circle.place(x=70, y=60, width=200, height=200)

        self.counter_ClearDaylabel = tk.Label(self, text="", font=("Segoe UI", 44, "bold"), fg= "#22223b", bg="#66ff66")
        self.counter_ClearDaylabel.place(x=170, y=160, anchor="center")

        tk.Button(self, image=self.img_back, command=self.Back, borderwidth=0, bg="#22223b", activebackground="#4a4e69").place(x=200, y=340, width=90, height=65)
        tk.Button(self, image=self.img_what, command=self.infoTrueNoPaf, borderwidth=0, bg="#22223b", activebackground="#4a4e69").place(x=50, y=340, width=90, height=60)         
 
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        yesterday_count = self.get_tyagi(yesterday)
        if yesterday_count == 0: 
            self.CounterDayWithNotyag += 1
            self.true_nopaf_circle.config(image=self.circle_green)
            self.counter_ClearDaylabel.config(text=str(self.CounterDayWithNotyag),fg= "#22223b", bg="#66ff66")
        else: 
            self.CounterDayWithNotyag = 0
            self.true_nopaf_circle.config(image=self.circle_red)
            self.counter_ClearDaylabel.config(text=str(self.CounterDayWithNotyag), fg="#22223b", bg="#ff6666")

    def bind_pause_key(self):
        def listen():
            keyboard.add_hotkey("pause", lambda: self.add_tyagi(threadsafe=True))
            keyboard.wait()
        threading.Thread(target=listen, daemon=True).start()
    

if __name__ == "__main__":
    app = NoPafApp()
    app.mainloop()