import tkinter as tk
from tkinter import messagebox
import random

class Game:
    def __init__(self, master, width=10, height=10, mines=10):
        self.master = master
        self.width = width
        self.height = height
        self.mines = mines
        self.buttons = {}
        self.revealed = set()
        self.flags = set()
        self.mine_positions = set()
        self.first_click = True
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError

    def place_mines(self, first_click_x, first_click_y):
        while len(self.mine_positions) < self.mines:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) != (first_click_x, first_click_y) and (x, y) not in self.mine_positions:
                self.mine_positions.add((x, y))

    def reveal(self, x, y):
        raise NotImplementedError

    def game_over(self, won):
        for (x, y) in self.mine_positions:
            self.buttons[(x, y)]['text'] = '💣'
            self.buttons[(x, y)]['bg'] = 'red'

        if won:
            msg = "Вы выиграли!"
        else:
            msg = "Вы проиграли!"

        messagebox.showinfo("Конец игры", msg)

        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

class Minesweeper(Game):
    def __init__(self, master, width=10, height=10, mines=10):
        super().__init__(master, width, height, mines)

    def create_widgets(self):
        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.pack(padx=20, pady=20)

        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=10)

        self.restart_button = tk.Button(
            control_frame,
            text="Перезапустить",
            command=self.restart_game,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            width=15
        )
        self.restart_button.pack(side=tk.LEFT, padx=5)

        for y in range(self.height):
            for x in range(self.width):
                button = tk.Button(
                    self.grid_frame,
                    width=4,
                    height=2,
                    font=("Arial", 12),
                    command=lambda x=x, y=y: self.reveal(x, y),
                    bg="#f0f0f0"
                )
                button.bind('<Button-3>', lambda event, x=x, y=y: self.toggle_flag(x, y))
                button.grid(row=y, column=x, padx=2, pady=2)
                self.buttons[(x, y)] = button

    def reveal(self, x, y):
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        if (x, y) in self.flags or (x, y) in self.revealed:
            return

        if (x, y) in self.mine_positions:
            self.buttons[(x, y)]['text'] = '💣'
            self.buttons[(x, y)]['bg'] = 'orange'
            self.revealed.add((x, y))
            self.game_over(False)
            return

        self.expose(x, y)
        self.check_win()

    def expose(self, x, y):
        if (x, y) in self.revealed or not self.in_bounds(x, y):
            return

        self.revealed.add((x, y))
        adjacent_mines = self.count_adjacent_mines(x, y)

        self.buttons[(x, y)]['text'] = str(adjacent_mines) if adjacent_mines > 0 else ''
        self.buttons[(x, y)]['bg'] = '#D3D3D3'

        if adjacent_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.expose(x + dx, y + dy)

    def toggle_flag(self, x, y):
        if (x, y) in self.revealed:
            return

        if len(self.flags) >= self.mines:
            messagebox.showwarning("Ограничение", "Вы установили все возможные флаги!")
            return


        if (x, y) in self.flags:
            self.buttons[(x, y)]['text'] = ''
            self.buttons[(x, y)]['bg'] = "#f0f0f0"
            self.flags.remove((x, y))
        else:
            self.buttons[(x, y)]['text'] = '🚩'
            self.buttons[(x, y)]['bg'] = "#FFEB3B"
            self.flags.add((x, y))

        self.check_win()

    def check_win(self):
        if len(self.revealed) == self.width * self.height - len(self.mine_positions):
            self.game_over(True)
        elif len(self.flags) == self.mines and all((x, y) in self.flags for (x, y) in self.mine_positions):
            self.game_over(True)

    def restart_game(self):
        self.master.destroy()
        start_game(self.width, self.height, self.mines)

def start_game(width, height, mines):
    root = tk.Tk()
    root.title("Сапер")
    Minesweeper(root, width, height, mines)
    root.mainloop()

def main_menu():
    menu_root = tk.Tk()
    menu_root.title("Сапер - Меню")
    menu_root.geometry('400x400')
    menu_root.config(bg="#f0f0f0")

    tk.Label(menu_root, text="Сапер", bg="#f0f0f0", font=("Arial", 24, "bold")).pack(pady=20)

    width_entry = tk.Entry(menu_root, font=("Arial", 12))
    width_entry.insert(0, "10")
    width_entry.pack(pady=5)

    height_entry = tk.Entry(menu_root, font=("Arial", 12))
    height_entry.insert(0, "10")
    height_entry.pack(pady=5)

    mines_entry = tk.Entry(menu_root, font=("Arial", 12))
    mines_entry.insert(0, "10")
    mines_entry.pack(pady=5)

    def start_game_with_custom_settings():
        try:
            width = int(width_entry.get())
            height = int(height_entry.get())
            mines = int(mines_entry.get())

            if width <= 0 or height <= 0 or mines <= 0 or mines > width * height:
                raise ValueError

            start_game(width, height, mines)
            menu_root.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите правильные значения.")

    tk.Button(menu_root, text="Начать игру", command=start_game_with_custom_settings, bg="#4CAF50", fg="white",
              font=("Arial", 14), width=15).pack(pady=20)

    menu_root.mainloop()

main_menu()
