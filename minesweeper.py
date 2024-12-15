import tkinter as tk
from tkinter import messagebox
import random

# Класс для игры "Сапер"
class Minesweeper:
    def __init__(self, master, width=10, height=10, mines=10):
        self.master = master  # Главное окно
        self.width = width  # Ширина поля
        self.height = height  # Высота поля
        self.mines = mines  # Количество мин

        # Игровое состояние
        self.buttons = {}  # Кнопки, соответствующие ячейкам поля
        self.revealed = set()  # Множество раскрытых ячеек
        self.flags = set()  # Множество установленных флагов
        self.mine_positions = set()  # Множество позиций мин
        self.first_click = True  # Флаг первого клика
        self.correct_flags = 0  # Количество правильно установленных флагов
        self.mines_stepped_on = 0  # Количество наступлений на мину
        self.flags_placed = 0  # Количество установленных флагов

        self.create_widgets()  # Создание виджетов на экране

    # Метод для создания виджетов (кнопок) на экране
    def create_widgets(self):
        self.grid_frame = tk.Frame(self.master)  # Создание контейнера для игрового поля
        self.grid_frame.pack(padx=20, pady=20)

        control_frame = tk.Frame(self.master)  # Панель управления (кнопка перезапуска)
        control_frame.pack(pady=10)

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

        # Создание кнопок для игрового поля
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
                # Правый клик для установки/снятия флага
                button.bind('<Button-3>', lambda event, x=x, y=y: self.toggle_flag(x, y))
                button.grid(row=y, column=x, padx=2, pady=2)  # Размещение кнопок на поле
                self.buttons[(x, y)] = button  # Сохранение кнопки в словарь

    # Метод для размещения мин на поле
    def place_mines(self, first_click_x, first_click_y):
        while len(self.mine_positions) < self.mines:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            # Мин не должно быть в том месте, где был сделан первый клик
            if (x, y) != (first_click_x, first_click_y) and (x, y) not in self.mine_positions:
                self.mine_positions.add((x, y))  # Размещение мины

    # Метод для раскрытия ячейки
    def reveal(self, x, y):
        if self.first_click:
            self.place_mines(x, y)  # Размещение мин при первом клике
            self.first_click = False  # Убираем флаг первого клика

        if (x, y) in self.flags or (x, y) in self.revealed:
            return  # Ячейка уже раскрыта или помечена флагом

        if (x, y) in self.mine_positions:
            self.mines_stepped_on += 1  # Увеличиваем счетчик наступлений на мину
            self.buttons[(x, y)]['text'] = '💣'  # Отображаем мину на кнопке
            self.buttons[(x, y)]['bg'] = 'orange'  # Меняем цвет фона кнопки
            self.revealed.add((x, y))  # Добавляем в список раскрытых ячеек
            self.check_all_mines_stepped()  # Проверяем, все ли мины подорваны
            return

        self.expose(x, y)   
        self.check_win()  # Проверка выигрыша

    
    def expose(self, x, y):
        if (x, y) in self.revealed or not self.in_bounds(x, y):
            return  # Если ячейка уже раскрыта или выходит за пределы поля

        self.revealed.add((x, y))  # Добавляем ячейку в раскрытые
        adjacent_mines = self.count_adjacent_mines(x, y)  # Считаем соседние мины

        # Отображаем количество соседних мин, если их больше 0
        self.buttons[(x, y)]['text'] = str(adjacent_mines) if adjacent_mines > 0 else ''
        self.buttons[(x, y)]['bg'] = '#D3D3D3'  # Меняем цвет фона

        # Если соседей мин нет, рекурсивно раскрываем соседние ячейки
        if adjacent_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.expose(x + dx, y + dy)

    # Метод для установки флага на ячейку
    def toggle_flag(self, x, y):
        if (x, y) in self.revealed:
            return  # Невозможно поставить флаг на раскрытую ячейку

        if self.flags_placed >= self.mines:
            messagebox.showwarning("Ограничение", "Вы установили все возможные флаги!")  # Ограничение по флагам
            return

        if (x, y) in self.flags:
            self.buttons[(x, y)]['text'] = ''  
            self.buttons[(x, y)]['bg'] = "#f0f0f0"  
            self.flags.remove((x, y))  
            self.flags_placed -= 1  
            if (x, y) in self.mine_positions:
                self.correct_flags -= 1  # Уменьшаем количество правильных флагов
        else:
            self.buttons[(x, y)]['text'] = '🚩'  
            self.buttons[(x, y)]['bg'] = "#FFEB3B"  
            self.flags.add((x, y))  
            self.flags_placed += 1  
            if (x, y) in self.mine_positions:
                self.correct_flags += 1  

        self.check_win()  # Проверка выигрыша

    # Метод для подсчета соседних мин
    def count_adjacent_mines(self, x, y):
        return sum((nx, ny) in self.mine_positions
                   for nx in range(x - 1, x + 2)
                   for ny in range(y - 1, y + 2)
                   if self.in_bounds(nx, ny))

    # Метод для проверки, находится ли ячейка в пределах поля
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    # Метод для проверки, выиграл ли игрок
    def check_win(self):
        if len(self.revealed) == self.width * self.height - len(self.mine_positions):
            self.game_over(True)  # Если все ячейки раскрыты, кроме мин
        elif self.correct_flags == self.mines and len(self.flags) == self.mines:
            self.game_over(True)  # Если все флаги установлены правильно

    # Метод для проверки, все ли мины подорваны
    def check_all_mines_stepped(self):
        if self.mines_stepped_on == len(self.mine_positions):
            self.game_over(False)  # Если наступили на все мины

    # Метод для завершения игры
    def game_over(self, won):
        for (x, y) in self.mine_positions:
            self.buttons[(x, y)]['text'] = '💣'  # Отображаем все мины
            self.buttons[(x, y)]['bg'] = 'red'  # Меняем цвет фона на красный

        if won:
            msg = f"Вы выиграли! Найдено мин: {self.correct_flags}, Наступлено на мин: {self.mines_stepped_on}"
        else:
            msg = f"Вы проиграли! Найдено мин: {self.correct_flags}, Наступлено на мин: {self.mines_stepped_on}"
        
        messagebox.showinfo("Конец игры", msg)  # Показываем сообщение о завершении игры

        # Блокируем все кнопки после окончания игры
        for button in self.buttons.values():
            button.config(state=tk.DISABLED)

    # Метод для перезапуска игры
    def restart_game(self):
        self.master.destroy()  # Закрываем текущее окно
        start_game(self.width, self.height, self.mines)  # Запускаем новую игру


# Функция для старта игры
def start_game(width, height, mines):
    root = tk.Tk()  # Создаем новое окно
    root.title("Сапер") 
    Minesweeper(root, width, height, mines) 
    root.mainloop()  


# Функция для отображения главного меню
def main_menu():
    menu_root = tk.Tk()  # Создаем окно меню
    menu_root.title("Сапер - Меню") 
    menu_root.geometry('400x400')  
    menu_root.config(bg="#f0f0f0")   

    tk.Label(menu_root, text="Сапер", bg="#f0f0f0", font=("Arial", 24, "bold")).pack(pady=20)

    # Поля для ввода ширины, высоты и количества мин
    tk.Label(menu_root, text="Ширина:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
    width_entry = tk.Entry(menu_root, font=("Arial", 12))
    width_entry.insert(0, "10")  # Значение по умолчанию
    width_entry.pack(pady=5)

    tk.Label(menu_root, text="Высота:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
    height_entry = tk.Entry(menu_root, font=("Arial", 12))
    height_entry.insert(0, "10")  # Значение по умолчанию
    height_entry.pack(pady=5)

    tk.Label(menu_root, text="Количество мин:", bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
    mines_entry = tk.Entry(menu_root, font=("Arial", 12))
    mines_entry.insert(0, "10")  # Значение по умолчанию
    mines_entry.pack(pady=5)

    # Функция для старта игры с пользовательскими настройками
    def start_game_with_custom_settings():
        try:
            width = int(width_entry.get())  # Получаем ширину
            height = int(height_entry.get())  # Получаем высоту
            mines = int(mines_entry.get())  # Получаем количество мин

            # Проверка валидности введенных данных
            if width <= 0 or height <= 0 or mines <= 0 or mines > width * height:
                raise ValueError

            start_game(width, height, mines)  # Запускаем игру
            menu_root.destroy()  # Закрываем меню
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите правильные значения для ширины, высоты и количества мин.")

    # Кнопка для старта игры
    tk.Button(menu_root, text="Начать игру", command=start_game_with_custom_settings, bg="#4CAF50", fg="white",
              font=("Arial", 14), width=15).pack(pady=20)

    menu_root.mainloop()  # Запуск главного цикла меню


main_menu()  # Запуск главного меню
