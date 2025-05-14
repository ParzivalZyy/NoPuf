import tkinter as tk
from tkinter import ttk, messagebox 
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import sqlite3
from datetime import date, timedelta
import threading
import keyboard


class NoPafApp(tk.Tk):
    def __init__(self):   
        super().__init__()  
        self.title("NoPaf")
        self.geometry("400x300")
        self.configure(bg="#FFFFFF")
        self.conn = sqlite3.connect("NoPaf.db")
        self.fontX = ("Arial", 16)
        self.last_checked_date = date.today().isoformat()
        self.current_bg = "#FFFFFF"

        self.CounterDayWithNotyag = 0

        self.configure_styles()
        self.create_tables()
        self.update_today_data()
        self.bind_pause_key()
        self.show_main_screen()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("Success.TButton", font=("Arial", 18), background="#28a745", anchor="center")  # Зеленая кнопка
        style.configure("Info.TButton", font=("Arial", 18), background="#17a2b8", anchor="center")    # Синяя кнопка
        style.configure("Warning.TButton", font=("Arial", 18), background="#ffc107", anchor="center") # Желтая кнопка

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

        self.counter_label = tk.Label(self, text="", font=("Arial", 40))
        self.counter_label.place(x=0, y=0, width=400, height=170)

        self.update_counter_color()

        self.create_button(" True\nNoPaf", self.TrueNoPaf, "Success.TButton", 0, 170, 100, 130)
        self.create_button("+1 Тяга", self.add_tyagi, "Info.TButton", 100, 170, 300, 65)
        self.create_button("Статистика", self.show_stats, "Warning.TButton", 100, 235, 300, 65)

    def get_tyagi(self, target_date):
        cursor = self.conn.cursor()
        cursor.execute("SELECT Тяги FROM Stats WHERE Дата = ?", (target_date,))
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def add_tyagi(self, threadsafe=False):
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        yesterday_count = self.get_tyagi(yesterday)

        def update_db():
            conn = sqlite3.connect("NoPaf.db") if threadsafe else self.conn
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO Stats (Дата, Тяги) VALUES (?, 0)", (today,))
            cursor.execute("UPDATE Stats SET Тяги = Тяги + 1 WHERE Дата = ?", (today,))
            if threadsafe:
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
            self.conn.commit()
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
            new_color = "#CCCCCC"  
        elif today_count < yesterday_count * 0.9:
            new_color = "#66ff66" 
        elif today_count < yesterday_count:
            new_color = "#ffff66"
        else:
            new_color = "#ff6666"

        self.counter_label.config(text=str(today_count), bg=new_color)

    def Back(self):
        self.clear_window()
        self.show_main_screen()

    def show_stats(self):
        self.check_new_day()
        self.clear_window()  
        self.create_button("Назад", self.Back, "Warning.TButton", 10, 10, 80, 45)
        tk.Label(self, text="Статистика", font=self.fontX, bg="#FFFFFF", fg="#004D40").place(x=130, y=0, width=140, height=65)
    
        stats_frame = tk.Frame(self, bg="#FFFFFF")
        stats_frame.place(x=0, y=65, width=400, height=235)
    
        scrollbar = ttk.Scrollbar(stats_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        tree = ttk.Treeview(stats_frame, columns=("Дата", "Тяги"), show="headings", yscrollcommand=scrollbar.set)
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
        
        self.counter_ClearDaylabel = tk.Label(self, text="", font=("Arial", 40))
        self.counter_ClearDaylabel.place(x=0, y=0, width=400, height=230)

        style = ttk.Style()
        style.configure("Info.TButton", font=("Arial", 16), background="#17a2b8", anchor="center")
        style.configure("Warning.TButton", font=("Arial", 18), background="#ffc107", anchor="center") # Желтая кнопка

        ttk.Button(self, text="Назад", command=self.Back, bootstyle=WARNING, style="Warning.TButton").place(x=80, y=230, width=320, height=70)
        ttk.Button(self, text="ЧаВо?", command=self.infoTrueNoPaf, bootstyle=INFO, style="Info.TButton").place(x=0, y=230, width=80, height=70)         
     
     # TODO:автоматический подсчёт дней, когда программа не открыта

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