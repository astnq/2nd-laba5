import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, master, width=10, height=10, mines=10, random_after_first_click=True):
        # Инициализация игры с переданными параметрами
        self.master = master
        self.width = width
        self.height = height
        self.mines = mines
        self.random_after_first_click = random_after_first_click

        # Инициализация пустых словарей и множеств для управления состоянием игры
        self.buttons = {}
        self.revealed = set()
        self.flags = set()
        self.mine_positions = set()
        self.first_click = True  # Для того, чтобы мины размещались только после первого клика
        self.mines_steped_on = 0  # Счётчик того, сколько раз игрок наступил на мину

        self.create_widgets()  # Инициализация интерфейса игры

    def create_widgets(self):
        # Создание основной сетки игры и кнопки перезапуска
        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.pack(padx=20, pady=20)

        self.restart_button = tk.Button(self.master, text="Перезапустить", command=self.restart_game, relief="raised", width=12, height=2, bg="#4CAF50", fg="white", font=("Arial", 12))
        self.restart_button.pack(pady=10)

        # Создание кнопок для каждой ячейки в сетке
        for y in range(self.height):
            for x in range(self.width):
                button = tk.Button(
                    self.grid_frame,
                    width=4,
                    height=2,
                    command=lambda x=x, y=y: self.reveal(x, y),  # Открыть ячейку при клике
                    font=("Arial", 12),
                    bg="#f0f0f0",  # Цвет фона по умолчанию
                )
                button.bind('<Button-3>', lambda event, x=x, y=y: self.toggle_flag(x, y))  # Правый клик для флажка
                button.grid(row=y, column=x, padx=2, pady=2)
                self.buttons[(x, y)] = button  # Сохраняем ссылку на кнопку в словарь

    def place_mines(self, first_click_x=None, first_click_y=None):
        # Размещение мин случайным образом на поле, исключая клетку с первым кликом
        while len(self.mine_positions) < self.mines:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) != (first_click_x, first_click_y):  # Убедиться, что первая клетка не является миной
                self.mine_positions.add((x, y))

    def reveal(self, x, y):
        # Логика для открытия клетки
        if self.first_click and self.random_after_first_click:
            self.place_mines(x, y)  # Размещаем мины после первого клика
            self.first_click = False

        if (x, y) in self.flags or (x, y) in self.revealed:
            return  # Пропускаем, если клетка уже открыта или помечена флажком

        if (x, y) in self.mine_positions:
            # Увеличиваем счётчик количества наступлений на мины
            self.mines_steped_on += 1
            # Показываем сообщение, но даём возможность продолжить игру
            self.buttons[(x, y)]['text'] = '*'
            self.buttons[(x, y)]['bg'] = 'red'  # Цвет для открытой мины
            messagebox.showinfo("Мина!", f"Вы наступили на {self.mines_steped_on} из {self.mines} мин!")
        else:
            self.expose(x, y)  # Открываем пустую клетку

        # Проверяем, все ли мины помечены флажками
        if len(self.flags) == self.mines:
            self.game_over(False)

        # Проверяем, открыл ли игрок все клетки без мин
        if len(self.revealed) == self.width * self.height - self.mines:
            self.game_over(True)

    def expose(self, x, y):
        # Открытие клетки и соседних клеток, если рядом нет мин
        if (x, y) in self.revealed or not self.in_bounds(x, y):
            return

        self.revealed.add((x, y))
        adjacent_mines = self.count_adjacent_mines(x, y)

        # Устанавливаем текст кнопки в зависимости от количества соседних мин
        self.buttons[(x, y)]['text'] = str(adjacent_mines) if adjacent_mines > 0 else ''
        self.buttons[(x, y)]['bg'] = '#D3D3D3'  # Цвет для открытых (не минных) клеток

        # Если нет соседних мин, рекурсивно открываем соседние клетки
        if adjacent_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.expose(x + dx, y + dy)

    def toggle_flag(self, x, y):
        # Переключение флажка на клетке (правый клик)
        if (x, y) in self.revealed:
            return  # Невозможно поставить флажок на открытую клетку

        if (x, y) in self.flags:
            self.buttons[(x, y)]['text'] = ''
            self.buttons[(x, y)]['bg'] = "#f0f0f0"  # Сброс цвета, если флажок снят
            self.flags.remove((x, y))
        else:
            self.buttons[(x, y)]['text'] = '🚩'
            self.buttons[(x, y)]['bg'] = "#FFEB3B"  # Цвет для клеток с флажком
            self.flags.add((x, y))

    def count_adjacent_mines(self, x, y):
        # Подсчитываем количество мин, соседствующих с данной клеткой
        return sum((nx, ny) in self.mine_positions
                   for nx in range(x - 1, x + 2)
                   for ny in range(y - 1, y + 2)
                   if self.in_bounds(nx, ny))

    def in_bounds(self, x, y):
        # Проверка, находится ли клетка в пределах игрового поля
        return 0 <= x < self.width and 0 <= y < self.height

    def game_over(self, won):
        # Окончание игры, показываем все мины
        for (x, y) in self.mine_positions:
            self.buttons[(x, y)]['text'] = '*'
            self.buttons[(x, y)]['bg'] = 'red'

        found_mines = len(self.flags & self.mine_positions)

        # Сообщение о победе (без счётчика "наступлений на мину", только найденные мины)
        if won:
            msg = ("Вы выиграли! Поздравляем, "
                "Вы наступили на {} мин(ы). ".format(self.mines_steped_on, found_mines, self.mines))
        else:
            # Сообщение о проигрыше с учётом счётчика "наступлений на мину"
            msg = ("Вы проиграли! Вы наступили на {} мин(ы). ".format(self.mines_steped_on, found_mines, self.mines))

        messagebox.showinfo("Конец игры", msg)

    def restart_game(self):
        # Перезапуск игры
        self.master.destroy()
        start_game(self.width, self.height, self.mines, self.random_after_first_click)

def start_game(width, height, mines, random_after_first_click):
    # Запуск игры
    root = tk.Tk()
    root.title("Сапер")
    app = Minesweeper(root, width, height, mines, random_after_first_click)
    root.mainloop()

def main_menu():
    
    menu_root = tk.Tk()  # Создаем новое окно для главного меню
    menu_root.title("Сапер - Меню")  # Устанавливаем заголовок окна

    menu_root.geometry('400x350')  # Устанавливаем размер окна
    menu_root.config(bg="#f0f0f0")  # Устанавливаем фоновый цвет окна

    
    title_label = tk.Label(menu_root, text="Сапер", bg="#f0f0f0", font=("Arial", 24, "bold"))
    title_label.pack(pady=20)  # Размещаем заголовок в окне с отступами


    tk.Label(menu_root, text="Выберите размер сетки и количество мин", bg="#f0f0f0", font=("Arial", 12)).pack(pady=10)

    tk.Label(menu_root, text="Ширина:", bg="#f0f0f0", font=("Arial", 12)).pack()  # Текстовое поле "Ширина"
    width_entry = tk.Entry(menu_root, font=("Arial", 12))  # Поле для ввода значения ширины
    width_entry.pack()  # Размещаем поле ввода
    width_entry.insert(0, '10')  # Устанавливаем значение по умолчанию (10)

    tk.Label(menu_root, text="Высота:", bg="#f0f0f0", font=("Arial", 12)).pack()  # Текстовое поле "Высота"
    height_entry = tk.Entry(menu_root, font=("Arial", 12))  # Поле для ввода значения высоты
    height_entry.pack()  # Размещаем поле ввода
    height_entry.insert(0, '10')  # Устанавливаем значение по умолчанию (10)

    tk.Label(menu_root, text="Мины:", bg="#f0f0f0", font=("Arial", 12)).pack()  # Текстовое поле "Мины"
    mines_entry = tk.Entry(menu_root, font=("Arial", 12))  # Поле для ввода количества мин
    mines_entry.pack()  # Размещаем поле ввода
    mines_entry.insert(0, '10')  # Устанавливаем значение по умолчанию (10)

    random_check = tk.BooleanVar()  # Переменная, которая будет хранить состояние чекбокса
    random_check.set(True)  # Устанавливаем значение по умолчанию как True (рандомное размещение)

    def start_from_menu():
        # Получаем значения из полей ввода
        width = int(width_entry.get())  # Ширина поля
        height = int(height_entry.get())  # Высота поля
        mines = int(mines_entry.get())  # Количество мин
        random_after_first_click = random_check.get()  # Состояние чекбокса
        menu_root.destroy()  # Закрываем главное меню
        start_game(width, height, mines, random_after_first_click)  # Запускаем игру с выбранными параметрами

    start_button = tk.Button(menu_root, text="Начать игру", command=start_from_menu, relief="raised", width=15, height=2, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
    start_button.pack(pady=20)  # Размещаем кнопку на экране

    menu_root.mainloop()  # Запуск главного меню игры

