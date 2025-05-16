import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import sqlite3
from datetime import date, timedelta, datetime
import threading
import keyboard
from PIL import Image, ImageTk

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

        self.img_true_nopaf = Image.open("pictures/True NoPaf.png").resize((110, 70), Image.LANCZOS)
        self.img_true_nopaf = ImageTk.PhotoImage(self.img_true_nopaf)
        self.img_plus = Image.open("pictures/1Plus.png").resize((130, 70), Image.LANCZOS)
        self.img_plus = ImageTk.PhotoImage(self.img_plus)
        self.img_stats = Image.open("pictures/Stats.png").resize((110, 70), Image.LANCZOS)
        self.img_stats = ImageTk.PhotoImage(self.img_stats)
        self.img_back = Image.open("pictures/Back.png").resize((135, 80), Image.LANCZOS)
        self.img_back = ImageTk.PhotoImage(self.img_back)
        self.img_what = Image.open("pictures/What.png").resize((135, 80), Image.LANCZOS)
        self.img_what = ImageTk.PhotoImage(self.img_what)
        
        self.circle_white = ImageTk.PhotoImage(Image.open("pictures/circle_white.png").resize((200, 200), Image.LANCZOS))
        self.circle_green = ImageTk.PhotoImage(Image.open("pictures/circle_green.png").resize((200, 200), Image.LANCZOS))
        self.circle_yellow = ImageTk.PhotoImage(Image.open("pictures/circle_yellow.png").resize((200, 200), Image.LANCZOS))
        self.circle_red = ImageTk.PhotoImage(Image.open("pictures/circle_red.png").resize((200, 200), Image.LANCZOS))

        self.create_tables()
        self.update_today_data()
        self.bind_pause_key()
        self.show_main_screen()


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

        self.circle_label = tk.Label(self, image=self.circle_white, bg="#2b3e4f", bd=0)
        self.circle_label.place(x=70, y=100, width=200, height=200)
        
        self.counter_text_label = tk.Label(self, text="", font=("Segoe UI", 34, "bold"), fg="#2F2C2C", bg="#2b3e4f")
        self.counter_text_label.place(x=170, y=200, anchor="center", width=80, height=50)

        self.interval_label = tk.Label(self, text="", font=("Segoe UI", 12), fg="#ffffff", bg="#2b3e4f")
        self.interval_label.place(x=170, y=320, anchor="center")
        
        self.update_counter_color()

        tk.Button(self, image=self.img_true_nopaf, command=self.TrueNoPaf, borderwidth=0, bg="#2b3e4f", activebackground="#2b3e4f").place(x=20, y=10, width=110, height=70)
        tk.Button(self, image=self.img_stats, command=self.show_stats, borderwidth=0, bg="#2b3e4f", activebackground="#2b3e4f").place(x=210, y=10, width=110, height=70)  
        tk.Button(self, image=self.img_plus, command=self.add_tyagi, borderwidth=0, bg="#2b3e4f", activebackground="#2b3e4f").place(x=110, y=360, width=120, height=60)

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
            circle_img = self.circle_white
            counter_bg = "#ffffff"
            interval_text = ""
        elif today_count < yesterday_count * 0.9:
            circle_img = self.circle_green
            counter_bg = "#66ff66"
            remaining_puffs = int(yesterday_count * 0.9) - today_count
            remaining_hours = (24 - datetime.now().hour)
            if remaining_puffs > 0 and remaining_hours > 0:
                minutes_per_puff = (remaining_hours * 60) / (remaining_puffs + 1)
                hours = int(minutes_per_puff // 60)
                minutes = int(minutes_per_puff % 60)
                interval_text = f"Рекомендуемый интервал - {hours}ч {minutes}мин"
            else:
                interval_text = ""
        elif today_count < yesterday_count:
            circle_img = self.circle_yellow
            counter_bg = "#ffff66"
            interval_text = ""
        else:
            circle_img = self.circle_red
            counter_bg = "#ff6666"
            interval_text = ""

        self.circle_label.config(image=circle_img)
        self.circle_label.image = circle_img
        self.counter_text_label.config(text=str(today_count), bg=counter_bg, fg="#2F2C2C")
        self.interval_label.config(text=interval_text)

    def update_counter_canvas(self, value, color):
        self.circle_label.config(image=self.circle_white if color == "#b5b6bb" else self.circle_green if color == "#66ff66" else self.circle_yellow if color == "#ffff66" else self.circle_red)
        self.counter_text_label.config(text=str(value), bg=color)

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

        tk.Button(self, image=self.img_back, command=self.Back, borderwidth=0, bg="#22223b", activebackground="#22223b").place(x=115, y=400, width=106, height=60)

    def infoTrueNoPaf(self):
        messagebox.showinfo("True NoPaf", "В этом режиме приложения будут автоматически считаться дни без затяжек подряд") 

    def TrueNoPaf(self):
        self.clear_window()
        self.counter_ClearDaylabel = tk.Label(self, text="", font=("Segoe UI", 44, "bold"), bg="#4a4e69", fg="#22223b")
        self.counter_ClearDaylabel.place(x=20, y=80, width=300, height=120)

        tk.Button(self, image=self.img_back, command=self.Back, borderwidth=0, bg="#22223b", activebackground="#4a4e69").place(x=200, y=290, width=90, height=60)
        tk.Button(self, image=self.img_what, command=self.infoTrueNoPaf, borderwidth=0, bg="#22223b", activebackground="#4a4e69").place(x=50, y=290, width=90, height=60)         
     
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        yesterday_count = self.get_tyagi(yesterday)
        if yesterday_count == 0: 
            self.CounterDayWithNotyag += 1
            self.counter_ClearDaylabel.config(text=str(self.CounterDayWithNotyag), bg="#66ff66", fg="#22223b")
        else: 
            self.CounterDayWithNotyag = 0
            self.counter_ClearDaylabel.config(text=str(self.CounterDayWithNotyag), bg="#ff6666", fg="#22223b")

    def bind_pause_key(self):
        def listen():
            keyboard.add_hotkey("pause", lambda: self.add_tyagi(threadsafe=True))
            keyboard.wait()
        threading.Thread(target=listen, daemon=True).start()

if __name__ == "__main__":
    app = NoPafApp()
    app.mainloop()