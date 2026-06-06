import tkinter as tk
import json
import os
import random
import math

# ==================== КОНФИГУРАЦИЯ ====================
CELL_SIZE = 30
MAZE_WIDTH = 19
MAZE_HEIGHT = 21

# Лабиринт (1 - стена, 0 - точка, 2 - энерджайзер, 3 - пусто)
# ВСЕ строки должны быть ОДИНАКОВОЙ длины - 19 элементов
MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # строка 0
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # строка 1
    [1, 2, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 2, 1],  # строка 2
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1],  # строка 3
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],  # строка 4
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],  # строка 5
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],  # строка 6
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # строка 7
    [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],  # строка 8
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],  # строка 9
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],  # строка 10
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # строка 11
    [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1],  # строка 12
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # строка 13
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],  # строка 14
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],  # строка 15
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # строка 16
]

# Проверка количества строк
print(f"Количество строк в лабиринте: {len(MAZE)}")
print(f"Ожидается: {MAZE_HEIGHT}")

# Проверка длины каждой строки
for i, row in enumerate(MAZE):
    print(f"Строка {i}: длина {len(row)}, ожидается {MAZE_WIDTH}")
    if len(row) != MAZE_WIDTH:
        print(f"ОШИБКА: строка {i} имеет длину {len(row)} вместо {MAZE_WIDTH}")
        # Исправляем строку, дополняя или обрезая
        if len(row) < MAZE_WIDTH:
            MAZE[i] = row + [1] * (MAZE_WIDTH - len(row))
        else:
            MAZE[i] = row[:MAZE_WIDTH]

# Стартовые позиции
PACMAN_START = (1, 1)
GHOSTS_START = [
    (9, 9),  # Блинки - красный
    (8, 9),  # Пинки - розовый
    (10, 9),  # Инки - голубой
    (9, 8),  # Клайд - оранжевый
]

# Имена и цвета призраков
GHOST_NAMES = ["Блинки", "Пинки", "Инки", "Клайд"]
GHOST_COLORS = ["red", "pink", "cyan", "orange"]
GHOST_VULNERABLE_COLOR = "blue"


class Ghost:
    def __init__(self, x, y, name, color, ghost_type):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.name = name
        self.color = color
        self.type = ghost_type
        self.vulnerable = False


class PacmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Пакмен - Классическая аркадная игра")

        window_width = MAZE_WIDTH * CELL_SIZE + 20
        window_height = MAZE_HEIGHT * CELL_SIZE + 100
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        # Загрузка рекорда
        self.records_file = "records.json"
        self.high_score = self.load_high_score()

        # Игровые переменные
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False
        self.energizer_counter = 0

        # Позиция Пакмена
        self.pacman_x, self.pacman_y = PACMAN_START
        self.pacman_dir_x = 0
        self.pacman_dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0

        # Создание копии лабиринта для точек
        self.maze_dots = []
        for row in MAZE:
            self.maze_dots.append(row[:])

        # Создание призраков
        self.ghosts = []
        for i, (x, y) in enumerate(GHOSTS_START):
            ghost_type = i % 4
            self.ghosts.append(Ghost(x, y, GHOST_NAMES[i], GHOST_COLORS[i], ghost_type))

        # Создание интерфейса
        self.create_widgets()

        # Отрисовка
        self.draw_maze()
        self.draw_pacman()
        self.draw_ghosts()
        self.update_score_display()

        # Управление
        self.root.bind("<Key>", self.key_press)
        self.root.bind("<p>", self.toggle_pause)
        self.root.bind("<P>", self.toggle_pause)

        # Запуск игрового цикла
        self.game_loop()

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Верхняя панель
        self.top_frame = tk.Frame(self.root, bg="black")
        self.top_frame.pack(pady=10)

        self.score_label = tk.Label(self.top_frame, text=f"Счёт: {self.score}",
                                    font=("Arial", 14, "bold"), fg="white", bg="black")
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.lives_label = tk.Label(self.top_frame, text=f"Жизни: {'❤️' * self.lives}",
                                    font=("Arial", 14), fg="red", bg="black")
        self.lives_label.pack(side=tk.LEFT, padx=20)

        self.level_label = tk.Label(self.top_frame, text=f"Уровень: {self.level}",
                                    font=("Arial", 14, "bold"), fg="white", bg="black")
        self.level_label.pack(side=tk.LEFT, padx=20)

        self.high_score_label = tk.Label(self.top_frame, text=f"Рекорд: {self.high_score}",
                                         font=("Arial", 14, "bold"), fg="yellow", bg="black")
        self.high_score_label.pack(side=tk.LEFT, padx=20)

        # Игровое поле
        self.canvas = tk.Canvas(self.root, width=MAZE_WIDTH * CELL_SIZE,
                                height=MAZE_HEIGHT * CELL_SIZE, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Нижняя панель с управлением
        self.bottom_frame = tk.Frame(self.root, bg="black")
        self.bottom_frame.pack(pady=10)

        controls_text = "Управление: ← ↑ ↓ → | P - Пауза | R - Перезапуск"
        self.controls_label = tk.Label(self.bottom_frame, text=controls_text,
                                       font=("Arial", 10), fg="gray", bg="black")
        self.controls_label.pack()

    def load_high_score(self):
        """Загрузка рекорда из файла"""
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        """Сохранение рекорда в файл"""
        with open(self.records_file, "w", encoding="utf-8") as f:
            json.dump({"high_score": self.high_score}, f, ensure_ascii=False, indent=2)

    def draw_maze(self):
        """Отрисовка лабиринта, стен, точек и энерджайзеров"""
        for y in range(len(MAZE)):
            for x in range(len(MAZE[y])):
                if MAZE[y][x] == 1:  # Стена
                    self.canvas.create_rectangle(
                        x * CELL_SIZE, y * CELL_SIZE,
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                        fill="navy", outline="blue", width=1
                    )
                elif self.maze_dots[y][x] == 0:  # Точка
                    self.canvas.create_oval(
                        x * CELL_SIZE + CELL_SIZE // 2 - 2,
                        y * CELL_SIZE + CELL_SIZE // 2 - 2,
                        x * CELL_SIZE + CELL_SIZE // 2 + 2,
                        y * CELL_SIZE + CELL_SIZE // 2 + 2,
                        fill="white", tags=f"dot_{x}_{y}"
                    )
                elif self.maze_dots[y][x] == 2:  # Энерджайзер
                    self.canvas.create_oval(
                        x * CELL_SIZE + CELL_SIZE // 2 - 6,
                        y * CELL_SIZE + CELL_SIZE // 2 - 6,
                        x * CELL_SIZE + CELL_SIZE // 2 + 6,
                        y * CELL_SIZE + CELL_SIZE // 2 + 6,
                        fill="yellow", tags=f"energizer_{x}_{y}"
                    )

    def draw_pacman(self):
        """Отрисовка Пакмена"""
        self.canvas.delete("pacman")
        self.canvas.create_oval(
            self.pacman_x * CELL_SIZE + 4, self.pacman_y * CELL_SIZE + 4,
            (self.pacman_x + 1) * CELL_SIZE - 4, (self.pacman_y + 1) * CELL_SIZE - 4,
            fill="yellow", tags="pacman"
        )

    def draw_ghosts(self):
        """Отрисовка всех призраков"""
        self.canvas.delete("ghost")
        for ghost in self.ghosts:
            if ghost.vulnerable:
                color = GHOST_VULNERABLE_COLOR
            else:
                color = ghost.color
            self.canvas.create_rectangle(
                ghost.x * CELL_SIZE + 5, ghost.y * CELL_SIZE + 5,
                (ghost.x + 1) * CELL_SIZE - 5, (ghost.y + 1) * CELL_SIZE - 5,
                fill=color, tags="ghost"
            )
            # Глаза призрака
            self.canvas.create_oval(
                ghost.x * CELL_SIZE + 8, ghost.y * CELL_SIZE + 10,
                ghost.x * CELL_SIZE + 12, ghost.y * CELL_SIZE + 14,
                fill="white", tags="ghost"
            )
            self.canvas.create_oval(
                ghost.x * CELL_SIZE + 18, ghost.y * CELL_SIZE + 10,
                ghost.x * CELL_SIZE + 22, ghost.y * CELL_SIZE + 14,
                fill="white", tags="ghost"
            )

    def update_score_display(self):
        """Обновление отображения счёта, жизней и уровня"""
        self.score_label.config(text=f"Счёт: {self.score}")
        hearts = "❤️" * self.lives if self.lives > 0 else "💀"
        self.lives_label.config(text=f"Жизни: {hearts}")
        self.level_label.config(text=f"Уровень: {self.level}")
        self.high_score_label.config(text=f"Рекорд: {self.high_score}")

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.high_score_label.config(text=f"Рекорд: {self.high_score}")

    def check_dot_collision(self):
        """Проверка сбора точек и энерджайзеров"""
        x, y = self.pacman_x, self.pacman_y

        # Проверка границ
        if y < 0 or y >= len(self.maze_dots) or x < 0 or x >= len(self.maze_dots[y]):
            return

        if self.maze_dots[y][x] == 0:  # Обычная точка
            self.maze_dots[y][x] = 3
            self.canvas.delete(f"dot_{x}_{y}")
            self.score += 10
            self.update_score_display()
        elif self.maze_dots[y][x] == 2:  # Энерджайзер
            self.maze_dots[y][x] = 3
            self.canvas.delete(f"energizer_{x}_{y}")
            self.score += 50
            self.energizer_active = True
            self.energizer_counter = 100
            for ghost in self.ghosts:
                ghost.vulnerable = True
            self.update_score_display()

    def move_pacman(self):
        """Движение Пакмена"""
        x, y = self.pacman_x, self.pacman_y

        # Телепорты по бокам
        if y == 9:
            if x < 0:
                x = MAZE_WIDTH - 1
                self.pacman_x = x
            elif x >= MAZE_WIDTH:
                x = 0
                self.pacman_x = x

        # Попытка движения в запрошенном направлении
        nx, ny = x + self.next_dir_x, y + self.next_dir_y
        if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
            if MAZE[ny][nx] != 1:
                self.pacman_dir_x, self.pacman_dir_y = self.next_dir_x, self.next_dir_y
                self.pacman_x, self.pacman_y = nx, ny
                self.check_dot_collision()
                self.draw_pacman()
                return

        # Движение в текущем направлении
        nx, ny = x + self.pacman_dir_x, y + self.pacman_dir_y
        if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT:
            if MAZE[ny][nx] != 1:
                self.pacman_x, self.pacman_y = nx, ny
                self.check_dot_collision()
                self.draw_pacman()

    def move_ghosts_simple(self, ghost):
        """Простое движение призрака к Пакмену"""
        px, py = self.pacman_x, self.pacman_y
        gx, gy = ghost.x, ghost.y

        # Выбираем направление, приближающее к Пакмену
        dx_options = []
        dy_options = []

        if px > gx:
            dx_options.append(1)
        elif px < gx:
            dx_options.append(-1)

        if py > gy:
            dy_options.append(1)
        elif py < gy:
            dy_options.append(-1)

        # Пробуем движение по горизонтали
        for dx in dx_options:
            nx, ny = gx + dx, gy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and MAZE[ny][nx] != 1:
                ghost.x, ghost.y = nx, ny
                return

        # Пробуем движение по вертикали
        for dy in dy_options:
            nx, ny = gx, gy + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and MAZE[ny][nx] != 1:
                ghost.x, ghost.y = nx, ny
                return

        # Случайное движение
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and MAZE[ny][nx] != 1:
                ghost.x, ghost.y = nx, ny
                return

    def move_ghosts(self):
        """Движение всех призраков"""
        for ghost in self.ghosts:
            if ghost.vulnerable:
                # Уязвимые призраки убегают (случайное движение)
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                random.shuffle(dirs)
                for dx, dy in dirs:
                    nx, ny = ghost.x + dx, ghost.y + dy
                    if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and MAZE[ny][nx] != 1:
                        ghost.x, ghost.y = nx, ny
                        break
            else:
                self.move_ghosts_simple(ghost)

        self.draw_ghosts()

    def check_collision(self):
        """Проверка столкновений Пакмена с призраками"""
        for ghost in self.ghosts:
            if self.pacman_x == ghost.x and self.pacman_y == ghost.y:
                if ghost.vulnerable:
                    # Съедание призрака
                    self.score += 200
                    ghost.x, ghost.y = ghost.start_x, ghost.start_y
                    ghost.vulnerable = False
                    self.update_score_display()
                else:
                    # Потеря жизни
                    self.lives -= 1
                    self.update_score_display()
                    self.reset_positions()
                    if self.lives <= 0:
                        self.game_over = True
                    return

    def reset_positions(self):
        """Сброс позиций после потери жизни"""
        self.pacman_x, self.pacman_y = PACMAN_START
        self.pacman_dir_x = 0
        self.pacman_dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        for ghost in self.ghosts:
            ghost.x, ghost.y = ghost.start_x, ghost.start_y
            ghost.vulnerable = False
        self.energizer_active = False
        self.energizer_counter = 0
        self.draw_pacman()
        self.draw_ghosts()

    def check_win(self):
        """Проверка завершения уровня"""
        for y in range(len(self.maze_dots)):
            for x in range(len(self.maze_dots[y])):
                if self.maze_dots[y][x] in (0, 2):
                    return False
        return True

    def next_level(self):
        """Переход на следующий уровень"""
        self.level += 1
        self.score += 500
        self.maze_dots = []
        for row in MAZE:
            self.maze_dots.append(row[:])
        self.reset_positions()
        self.canvas.delete("all")
        self.draw_maze()
        self.draw_pacman()
        self.draw_ghosts()
        self.update_score_display()

    def game_loop(self):
        """Основной игровой цикл"""
        if self.game_over or self.win:
            return

        if not self.paused:
            # Обновление таймера энерджайзера
            if self.energizer_active:
                self.energizer_counter -= 1
                if self.energizer_counter <= 0:
                    self.energizer_active = False
                    for ghost in self.ghosts:
                        ghost.vulnerable = False

            self.move_pacman()
            self.move_ghosts()
            self.check_collision()

            if self.check_win():
                if self.level >= 5:
                    self.win = True
                    self.show_game_over()
                    return
                else:
                    self.next_level()

        self.root.after(120, self.game_loop)

    def key_press(self, event):
        """Обработка нажатий клавиш"""
        key = event.keysym
        if key == "Up":
            self.next_dir_x, self.next_dir_y = 0, -1
        elif key == "Down":
            self.next_dir_x, self.next_dir_y = 0, 1
        elif key == "Left":
            self.next_dir_x, self.next_dir_y = -1, 0
        elif key == "Right":
            self.next_dir_x, self.next_dir_y = 1, 0
        elif key == "r" or key == "R":
            self.restart_game()

    def toggle_pause(self, event=None):
        """Пауза игры"""
        if not self.game_over and not self.win:
            self.paused = not self.paused
            if self.paused:
                self.show_pause_message()
            else:
                self.canvas.delete("pause_text")

    def show_pause_message(self):
        """Отображение сообщения о паузе"""
        self.canvas.create_text(
            MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2,
            text="ПАУЗА\nНажмите P для продолжения",
            fill="white", font=("Arial", 20, "bold"), tags="pause_text"
        )

    def show_game_over(self):
        """Отображение окончания игры"""
        self.canvas.delete("all")

        if self.win:
            title = "ПОБЕДА!"
            color = "green"
        else:
            title = "ПОРАЖЕНИЕ"
            color = "red"

        self.canvas.create_text(
            MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2 - 40,
            text=title, fill=color, font=("Arial", 32, "bold")
        )
        self.canvas.create_text(
            MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2,
            text=f"Счёт: {self.score}", fill="white", font=("Arial", 20)
        )
        self.canvas.create_text(
            MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2 + 40,
            text=f"Рекорд: {self.high_score}", fill="yellow", font=("Arial", 16)
        )
        self.canvas.create_text(
            MAZE_WIDTH * CELL_SIZE // 2, MAZE_HEIGHT * CELL_SIZE // 2 + 90,
            text="Нажмите R для перезапуска", fill="gray", font=("Arial", 14)
        )

    def restart_game(self):
        """Полный перезапуск игры"""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False
        self.energizer_counter = 0

        self.maze_dots = []
        for row in MAZE:
            self.maze_dots.append(row[:])

        self.reset_positions()

        self.canvas.delete("all")
        self.draw_maze()
        self.draw_pacman()
        self.draw_ghosts()
        self.update_score_display()


if __name__ == "__main__":
    root = tk.Tk()
    game = PacmanGame(root)
    root.mainloop()