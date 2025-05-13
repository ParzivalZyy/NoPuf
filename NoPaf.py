import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import date, timedelta
import threading
import keyboard
from tkinter import messagebox 

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

        self.create_tables()
        self.update_today_data()
        self.bind_pause_key()
        self.show_main_screen()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Дата (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Дата DATE UNIQUE,
                Тяги INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS NoPaf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Data2 DATE UNIQUE,
                НетТягам INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def update_today_data(self):
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Дата (Дата, Тяги) VALUES (?, 0)", (today,))
        cursor.execute("INSERT OR IGNORE INTO NoPaf (Data2, НетТягам) VALUES (?, 0)", (today,))
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

        self.counter_label = tk.Label(self, text="", font=("Arial", 40))
        self.counter_label.place(x=0, y=0, width=400, height=127)

        self.update_counter_color()
        tk.Button(self, text="NoPaf", command=self.NoPafl, font=self.fontX, bg="white", fg="#000000").place(x=0, y=125, width=100, height=175)
        tk.Button(self, text="+1 Тяга", command=self.add_tyage, font=self.fontX, bg="white", fg="#000000").place(x=100, y=125, width=300, height=90)
        tk.Button(self, text="Статистика", command=self.show_stats, font=self.fontX, bg="white", fg="#000000").place(x=100, y=215, width=300, height=85)

    def get_tyagi(self, target_date):
        cursor = self.conn.cursor()
        cursor.execute("SELECT Тяги FROM Дата WHERE Дата = ?", (target_date,))
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def add_tyage(self, threadsafe=False):
        today = date.today().isoformat()

        def update_db(cursor):
            cursor.execute("INSERT OR IGNORE INTO Дата (Дата, Тяги) VALUES (?, 0)", (today,))
            cursor.execute("UPDATE Дата SET Тяги = Тяги + 1 WHERE Дата = ?", (today,))

        if threadsafe:
            def threaded_update():
                conn = sqlite3.connect("NoPaf.db")
                cursor = conn.cursor()
                update_db(cursor)
                conn.commit()
                conn.close()
                self.after(0, self.update_counter_color)

            threading.Thread(target=threaded_update, daemon=True).start()
        else:
            self.check_new_day()
            cursor = self.conn.cursor()
            update_db(cursor)
            self.conn.commit()
            self.update_counter_color()

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
            messagebox.showwarning("!!!!!!!!!!!!!!!!!!!!!!!!!", "СТОЯТЬ, ХУИЛА") 
        else:
            new_color = "#ff6666"
            messagebox.showwarning("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
                                    "Ты прекратишь заниматься этим дерьмом," \
            " или это придётся делать выжившим членам твоей семьи") 

        self.counter_label.config(text=str(today_count), bg=new_color)

    def Back(self):
        self.clear_window()
        self.show_main_screen()

    def show_stats(self):
        self.check_new_day()
        self.clear_window()  
    
        tk.Button(self, text="Назад", command=self.Back, font=self.fontX, bg="white", fg="#000000").place(x=0, y=0, width=80, height=65)
        tk.Label(self, text="Статистика", font=self.fontX, bg="#FFFFFF", fg="black").place(x=140, y=0, width=140, height=65)
    
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
        cursor.execute("SELECT Дата, Тяги FROM Дата ORDER BY Дата DESC")
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0], row[1]))

    def DayNoPaf(self):
        self.check_new_day()
        today = date.today().isoformat()
        conn = sqlite3.connect("NoPaf.db")
        cursor = conn.cursor()
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO NoPaf (Data2, НетТягам) VALUES (?, 0)", (today,))
        cursor.execute("UPDATE NoPaf SET НетТягам = НетТягам + 1 WHERE Data2 = ?", (today,))
        self.conn.commit()

    def infoTrueNoPaf(self):
        messagebox.showinfo("True NoPaf", "В этом режиме приложения будут автоматически считаться дни без затяжек, если их не было, но надо зайти в приложение") 

    def NoPafl(self):
        self.clear_window()
        tk.Button(self, text="Назад", command=self.Back, font=self.fontX, bg="white", fg="#000000").place(x=0, y=125, width=100, height=175)
        self.counter_label = tk.Label(self, text="", font=("Arial", 40))
        self.counter_label.place(x=0, y=0, width=400, height=127)
        tk.Button(self, text="Удалить кнопку", command=self.DayNoPaf, font=self.fontX, bg="white", fg="#000000").place(x=100, y=125, width=300, height=175)
        tk.Button(self, text="ЧаВо", command=self.infoTrueNoPaf, font=self.fontX, bg="white", fg="#000000").place(x=0, y=0, width=60, height=50)

    def bind_pause_key(self):
        def listen():
            keyboard.add_hotkey("pause", lambda: self.add_tyage(threadsafe=True))
            keyboard.wait()

        threading.Thread(target=listen, daemon=True).start()

if __name__ == "__main__":
    app = NoPafApp()  
    app.mainloop()