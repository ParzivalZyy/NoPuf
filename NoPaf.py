import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import date, timedelta
import threading
import keyboard

'не вставляй код c нейронки, который сам не можешь написать'
class NoPafApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NoPaf")
        self.root.geometry("400x300")
        self.root.configure(bg="#FFFFFF")
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
        self.conn.commit()

    def update_today_data(self):
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Дата (Дата, Тяги) VALUES (?, 0)", (today,))
        self.conn.commit()

    def check_new_day(self):
        current_date = date.today().isoformat()
        if self.last_checked_date != current_date:
            self.last_checked_date = current_date
            self.update_today_data()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_screen(self):
        self.check_new_day()
        self.clear_window()

        self.counter_label = tk.Label(self.root, text="", font=("Arial", 40))
        self.counter_label.place(x=0, y=0, width=400, height=125)

        self.update_counter_color()

        tk.Button(self.root, text="+1 Тяга", command=self.increment_tyage, font=self.fontX, bg="white", fg="#000000").place(x=0, y=125, width=405, height=80)
        tk.Button(self.root, text="Статистика", command=self.show_stats, font=self.fontX, bg="white", fg="#000000").place(x=0, y=220, width=405, height=80)

    def get_tyagi(self, target_date):
        cursor = self.conn.cursor()
        cursor.execute("SELECT Тяги FROM Дата WHERE Дата = ?", (target_date,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def increment_tyage(self):
        self.check_new_day()
        today = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Дата SET Тяги = Тяги + 1 WHERE Дата = ?", (today,))
        self.conn.commit()
        self.update_counter_color()

    def increment_tyage_threadsafe(self):
        today = date.today().isoformat()
        conn = sqlite3.connect("NoPaf.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Дата (Дата, Тяги) VALUES (?, 0)", (today,))
        cursor.execute("UPDATE Дата SET Тяги = Тяги + 1 WHERE Дата = ?", (today,))
        conn.commit()
        conn.close()
        self.safe_update_ui()

    def safe_update_ui(self):
        self.root.after(0, self.update_counter_color)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def transition_color(self, start, end, steps, step):
        return tuple(
            int(start[i] + (end[i] - start[i]) * step / steps) for i in range(3)
        )

    def animate_color_transition(self, from_color, to_color, steps=10, delay=30):
        from_rgb = self.hex_to_rgb(from_color)
        to_rgb = self.hex_to_rgb(to_color)

        def step_animation(step=0):
            if step > steps:
                self.current_bg = to_color
                return
            rgb = self.transition_color(from_rgb, to_rgb, steps, step)
            hex_color = self.rgb_to_hex(rgb)
            self.counter_label.config(bg=hex_color)
            self.root.after(delay, step_animation, step + 1)

        step_animation()

    def update_counter_color(self):
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today_count = self.get_tyagi(today)
        yesterday_count = self.get_tyagi(yesterday)

        if yesterday_count == 0:
            percent_change = 0
        else:
            percent_change = ((today_count - yesterday_count) / yesterday_count) * 100

        self.counter_label.config(text=str(today_count))

        if yesterday_count == 0:
            new_color = "#CCCCCC"
        elif percent_change <= -10:
            new_color = "#00cc66"  
        elif percent_change >= -5:
            new_color = "#ff6666"  
        else:
            new_color = "#ffff66"  

        self.animate_color_transition(self.current_bg, new_color)

    def Back(self):
        self.clear_window()
        self.show_main_screen()

    def show_stats(self):
        self.check_new_day()
        self.clear_window()
        tk.Button(self.root, text="Назад", command=self.Back, font=self.fontX, bg="white", fg="#000000").place(x=0, y=0, width=80, height=65)
        tk.Label(self.root, text="Статистика", font=self.fontX, bg="#FFFFFF", fg="black").pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(frame, columns=("Дата", "Тяги"), show="headings", yscrollcommand=scrollbar.set)
        tree.heading("Дата", text="Дата")
        tree.heading("Тяги", text="Тяги")
        tree.column("Дата", anchor="center")
        tree.column("Тяги", anchor="center")
        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=tree.yview)

        cursor = self.conn.cursor()
        cursor.execute("SELECT Дата, Тяги FROM Дата ORDER BY Дата DESC")
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0], row[1]))

        tk.Button(self.root, text="Назад", command=self.show_main_screen, font=self.fontX, bg="white", fg="#000000").pack(pady=20)

    def bind_pause_key(self):
        def listen():
            keyboard.add_hotkey("pause", self.increment_tyage_threadsafe)
            keyboard.wait()

        threading.Thread(target=listen, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = NoPafApp(root)
    root.mainloop()