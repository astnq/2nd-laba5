import tkinter as tk
from tkinter import messagebox
import random


class Minesweeper:
    def __init__(self, master, width=10, height=10, mines=10):
        self.master = master
        self.width = width
        self.height = height
        self.mines = mines

        # Игровое состояние: переменные для кнопок, раскрытых ячеек, флагов и позиций мин
        self.buttons = {}  # Словарь для кнопок
        self.revealed = set()  # Множество для раскрытых ячеек
        self.flags = set()  # Множество для флагов
        self.mine_positions = set()  # Множество для позиций мин
        self.first_click = True  # Флаг, показывающий, что это первый клик
        self.correct_flags = 0  # Количество правильно установленных флагов
        self.mines_stepped_on = 0  # Количество мин, на которые наступил игрок
        self.flag_mode = False  # Режим установки флагов (по умолчанию выключен)

        self.create_widgets()  # Создание всех виджетов и интерфейса

    def create_widgets(self):
        # Создание игрового поля
        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.pack(padx=20, pady=20)

        # Панель управления: кнопки для флагов и перезапуска
        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=10)

        # Кнопка для переключения режима флага
        self.flag_button = tk.Button(
            control_frame,
            text="Режим Флага: ВЫКЛ",
            command=self.toggle_flag_mode,
            bg="#FF5733",
            fg="white",
            font=("Arial", 12),
            width=15
        )
        self.flag_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для перезапуска игры
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

        # Создание сетки кнопок (игровое поле)
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
                # Правая кнопка мыши для установки флага
                button.bind('<Button-3>', lambda event, x=x, y=y: self.toggle_flag(x, y))
                button.grid(row=y, column=x, padx=2, pady=2)
                self.buttons[(x, y)] = button  # Сохраняем кнопку в словарь

    def toggle_flag_mode(self):
        # Переключение режима флага
        self.flag_mode = not self.flag_mode
        if self.flag_mode:
            self.flag_button.config(text="Режим Флага: ВКЛ", bg="#4CAF50")
        else:
            self.flag_button.config(text="Режим Флага: ВЫКЛ", bg="#FF5733")

    def place_mines(self, first_click_x, first_click_y):
        # Расположение мин случайным образом (не на первой нажатой ячейке)
        while len(self.mine_positions) < self.mines:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) != (first_click_x, first_click_y) and (x, y) not in self.mine_positions:
                self.mine_positions.add((x, y))  # Добавляем мину в случайную позицию

    def reveal(self, x, y):
        # Открытие ячейки
        if self.first_click:
            self.place_mines(x, y)  # Расставляем мины при первом клике
            self.first_click = False

        if (x, y) in self.flags or (x, y) in self.revealed:
            return  # Если ячейка уже помечена флагом или раскрыта, ничего не делать

        if self.flag_mode:
            self.toggle_flag(x, y)  # В режиме флага пытаемся установить флаг
            return

        if (x, y) in self.mine_positions:
            # Игрок наступил на мину
            self.mines_stepped_on += 1
            self.buttons[(x, y)]['text'] = '💣'
            self.buttons[(x, y)]['bg'] = 'orange'
            self.revealed.add((x, y))  # Добавляем ячейку в раскрытые
            self.check_all_mines_stepped()  # Проверка, наступил ли игрок на все мины
            return

        # Ячейка безопасна, открываем её
        self.expose(x, y)

        # Проверка победы
        self.check_win()

    def expose(self, x, y):
        # Раскрытие ячейки и её соседей (если вокруг нет мин)
        if (x, y) in self.revealed or not self.in_bounds(x, y):
            return

        self.revealed.add((x, y))
        adjacent_mines = self.count_adjacent_mines(x, y)

        # Устанавливаем текст и фон для ячейки
        self.buttons[(x, y)]['text'] = str(adjacent_mines) if adjacent_mines > 0 else ''
        self.buttons[(x, y)]['bg'] = '#D3D3D3'

        if adjacent_mines == 0:
            # Если вокруг нет мин, раскрываем все соседние ячейки
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.expose(x + dx, y + dy)

    def toggle_flag(self, x, y):
        # Установка или снятие флага
        if (x, y) in self.revealed:
            return  # Нельзя установить флаг на раскрытую ячейку

        if (x, y) in self.flags:
            self.buttons[(x, y)]['text'] = ''
            self.buttons[(x, y)]['bg'] = "#f0f0f0"
            self.flags.remove((x, y))  # Убираем флаг и обновляем количество правильно установленных флагов
            if (x, y) in self.mine_positions:
                self.correct_flags -= 1
        else:
            self.buttons[(x, y)]['text'] = '🚩'
            self.buttons[(x, y)]['bg'] = "#FFEB3B"
            self.flags.add((x, y))  # Добавляем флаг
            if (x, y) in self.mine_positions:
                self.correct_flags += 1  # Увеличиваем счетчик правильно установленных флагов

        # Проверка победы
        self.check_win()

    def count_adjacent_mines(self, x, y):
        # Подсчет количества мин в соседних ячейках
        return sum((nx, ny) in self.mine_positions
                   for nx in range(x - 1, x + 2)
                   for ny in range(y - 1, y + 2)
                   if self.in_bounds(nx, ny))

    def in_bounds(self, x, y):
        # Проверка, находится ли ячейка в пределах игрового поля
        return 0 <= x < self.width and 0 <= y < self.height

    def check_win(self):
        # Проверка победы: все безопасные ячейки открыты или все мины помечены флагами
        if len(self.revealed) == self.width * self.height - len(self.mine_positions):
            self.game_over(True)  # Игрок выиграл

    def check_all_mines_stepped(self):
        # Проверка, наступил ли игрок на все мины
        if self.mines_stepped_on == len(self.mine_positions):
            self.game_over(False)  # Игрок проиграл

    def game_over(self, won):
        # Завершение игры
        for (x, y) in self.mine_positions:
            self.buttons[(x, y)]['text'] = '💣'
            self.buttons[(x, y)]['bg'] = 'red'

        # Отображение сообщения о выигрыше или проигрыше
        msg = "Вы выиграли! " if won else f"Вы проиграли! Вы наступили на {self.mines_stepped_on} мин."
        messagebox.showinfo("Конец игры", msg)

        # Блокировка всех кнопок после завершения игры
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

    def restart_game(self):
        # Перезапуск игры
        self.master.destroy()  # Закрыть текущее окно
        start_game(self.width, self.height, self.mines)  # Запуск новой игры


def start_game(width, height, mines):
    # Запуск игры с заданными параметрами
    root = tk.Tk()
    root.title("Сапер")
    Minesweeper(root, width, height, mines)
    root.mainloop()


def main_menu():
    # Главное меню с выбором уровня сложности
    menu_root = tk.Tk()
    menu_root.title("Сапер - Меню")
    menu_root.geometry('400x400')
    menu_root.config(bg="#f0f0f0")

    tk.Label(menu_root, text="Сапер", bg="#f0f0f0", font=("Arial", 24, "bold")).pack(pady=20)

    def start_with_difficulty(difficulty):
        # Запуск игры с выбранной сложностью
        if difficulty == 'Easy':
            start_game(8, 8, 10)
        elif difficulty == 'Normal':
            start_game(16, 16, 40)
        elif difficulty == 'Hard':
            start_game(24, 24, 99)

    # Кнопки для выбора сложности
    tk.Button(menu_root, text="Легкий", command=lambda: start_with_difficulty('Easy'), bg="#4CAF50", fg="white",
              font=("Arial", 14), width=15).pack(pady=10)
    tk.Button(menu_root, text="Средний", command=lambda: start_with_difficulty('Normal'), bg="#FFC107", fg="black",
              font=("Arial", 14), width=15).pack(pady=10)
    tk.Button(menu_root, text="Сложный", command=lambda: start_with_difficulty('Hard'), bg="#F44336", fg="white",
              font=("Arial", 14), width=15).pack(pady=10)

    menu_root.mainloop()


main_menu()
