import tkinter as tk
from tkinter import messagebox, Toplevel, Scale, Label, Button, Frame
import json
import os
import random

# ==================== КОНФИГУРАЦИЯ ====================
CELL_SIZE = 25
DEFAULT_GAME_SPEED = 120

# Файлы
MAZE_FILE = "maze.txt"
RECORDS_FILE = "records.json"
SETTINGS_FILE = "settings.json"

# Цвета
WALL_COLOR = "navy"
DOT_COLOR = "white"
ENERGIZER_COLOR = "yellow"
PACMAN_COLOR = "yellow"
GHOST_COLORS = ["red", "pink", "cyan", "orange"]
BG_COLOR = "black"
GHOST_HOUSE_COLOR = "#4B0082"


class PacmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("ПАКМЕН")
        self.root.configure(bg=BG_COLOR)

        # Загрузка настроек
        self.load_settings()

        # Загрузка рекордов
        self.scores = self.load_scores()

        # Игровые переменные
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False
        self.game_speed = self.settings.get("game_speed", DEFAULT_GAME_SPEED)

        # Пакмен
        self.pacman_x = 0
        self.pacman_y = 0
        self.pacman_dir = (0, 0)
        self.pacman_next_dir = (0, 0)

        # Призраки
        self.ghosts = []

        # Лабиринт
        self.maze = []
        self.dots = []
        self.width = 0
        self.height = 0

        # Загрузка уровня
        self.load_level()

        # Интерфейс
        self.create_widgets()

        # Управление
        self.root.bind("<Key>", self.key_press)
        self.root.bind("<p>", self.toggle_pause)
        self.root.bind("<P>", self.toggle_pause)
        self.root.bind("<Escape>", self.exit_game)

        # Запуск игры
        self.show_start_menu()

    def load_settings(self):
        """Загрузка настроек из файла"""
        default_settings = {"game_speed": DEFAULT_GAME_SPEED}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
            self.save_settings()

    def save_settings(self):
        """Сохранение настроек"""
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def load_scores(self):
        """Загрузка таблицы рекордов"""
        if os.path.exists(RECORDS_FILE):
            try:
                with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("scores", [])
            except:
                return []
        return []

    def save_scores(self):
        """Сохранение таблицы рекордов"""
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]
        with open(RECORDS_FILE, "w", encoding="utf-8") as f:
            json.dump({"scores": self.scores}, f, ensure_ascii=False, indent=2)

    def add_score(self, player_name, score):
        """Добавление нового рекорда"""
        self.scores.append({"name": player_name, "score": score})
        self.save_scores()

    def load_level(self):
        """Загрузка лабиринта из файла"""
        filename = MAZE_FILE if self.current_level == 1 else f"level_{self.current_level}.txt"

        if not os.path.exists(filename):
            filename = MAZE_FILE

        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        self.height = len(lines)
        self.width = len(lines[0])

        self.maze = []
        self.dots = []
        ghost_positions = []

        for y, line in enumerate(lines):
            row = []
            dot_row = []
            for x, ch in enumerate(line):
                if ch == '#':
                    row.append(1)
                    dot_row.append(0)
                elif ch == '.':
                    row.append(0)
                    dot_row.append(1)
                elif ch == 'o':
                    row.append(0)
                    dot_row.append(2)
                elif ch == 'P':
                    row.append(0)
                    dot_row.append(0)
                    self.pacman_x = x
                    self.pacman_y = y
                    self.pacman_start_x = x
                    self.pacman_start_y = y
                elif ch == 'H':
                    row.append(0)
                    dot_row.append(0)
                    self.house_exit_x = x
                    self.house_exit_y = y
                    self.house_center_x = x
                    self.house_center_y = y - 2
                elif ch == 'B':
                    row.append(0)
                    dot_row.append(0)
                    ghost_positions.append((x, y, 0))
                elif ch == 'K':
                    row.append(0)
                    dot_row.append(0)
                    ghost_positions.append((x, y, 1))
                elif ch == 'I':
                    row.append(0)
                    dot_row.append(0)
                    ghost_positions.append((x, y, 2))
                elif ch == 'C':
                    row.append(0)
                    dot_row.append(0)
                    ghost_positions.append((x, y, 3))
                else:
                    row.append(0)
                    dot_row.append(0)
            self.maze.append(row)
            self.dots.append(dot_row)

        # Создание призраков
        self.ghosts = []
        for i, (x, y, t) in enumerate(ghost_positions):
            self.ghosts.append({
                "x": self.house_center_x,
                "y": self.house_center_y,
                "start_x": self.house_center_x,
                "start_y": self.house_center_y,
                "type": t,
                "color": GHOST_COLORS[t],
                "in_house": True,
                "exit_timer": 30 + i * 20,
                "dir": (1, 0),
                "vulnerable": False,
                "vulnerable_timer": 0
            })

        self.update_window()

    def update_window(self):
        """Обновление размера окна"""
        width = self.width * CELL_SIZE + 20
        height = self.height * CELL_SIZE + 100
        self.root.geometry(f"{width}x{height}")

    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель
        top = tk.Frame(self.root, bg=BG_COLOR)
        top.pack(pady=10)

        self.score_label = tk.Label(top, text=f"Счёт: 0", font=("Arial", 14, "bold"),
                                    fg="white", bg=BG_COLOR)
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.lives_label = tk.Label(top, text="Жизни: ❤️❤️❤️", font=("Arial", 14),
                                    fg="red", bg=BG_COLOR)
        self.lives_label.pack(side=tk.LEFT, padx=20)

        self.level_label = tk.Label(top, text="Уровень: 1", font=("Arial", 14, "bold"),
                                    fg="white", bg=BG_COLOR)
        self.level_label.pack(side=tk.LEFT, padx=20)

        # Игровое поле
        self.canvas = tk.Canvas(self.root, width=self.width * CELL_SIZE,
                                height=self.height * CELL_SIZE, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack()

        # Нижняя панель
        bottom = tk.Frame(self.root, bg=BG_COLOR)
        bottom.pack(pady=10)

        tk.Label(bottom, text="Управление: ← ↑ ↓ → | P - Пауза | R - Перезапуск | ESC - Выход",
                 font=("Arial", 10), fg="gray", bg=BG_COLOR).pack()

    def draw_maze(self):
        """Отрисовка лабиринта"""
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 1:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE, y * CELL_SIZE,
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                        fill=WALL_COLOR, outline="blue"
                    )
                elif self.dots[y][x] == 1:
                    self.canvas.create_oval(
                        x * CELL_SIZE + CELL_SIZE // 2 - 2,
                        y * CELL_SIZE + CELL_SIZE // 2 - 2,
                        x * CELL_SIZE + CELL_SIZE // 2 + 2,
                        y * CELL_SIZE + CELL_SIZE // 2 + 2,
                        fill=DOT_COLOR, tags=f"dot_{x}_{y}"
                    )
                elif self.dots[y][x] == 2:
                    self.canvas.create_oval(
                        x * CELL_SIZE + CELL_SIZE // 2 - 6,
                        y * CELL_SIZE + CELL_SIZE // 2 - 6,
                        x * CELL_SIZE + CELL_SIZE // 2 + 6,
                        y * CELL_SIZE + CELL_SIZE // 2 + 6,
                        fill=ENERGIZER_COLOR, tags=f"energizer_{x}_{y}"
                    )

        # Дом призраков
        if hasattr(self, 'house_center_x') and self.house_center_x:
            self.canvas.create_rectangle(
                (self.house_center_x - 3) * CELL_SIZE,
                (self.house_center_y - 2) * CELL_SIZE,
                (self.house_center_x + 4) * CELL_SIZE,
                (self.house_center_y + 3) * CELL_SIZE,
                fill=GHOST_HOUSE_COLOR, outline="purple", width=2
            )
            self.canvas.create_rectangle(
                self.house_exit_x * CELL_SIZE,
                self.house_exit_y * CELL_SIZE,
                (self.house_exit_x + 1) * CELL_SIZE,
                (self.house_exit_y + 1) * CELL_SIZE,
                fill="darkgreen", outline="lightgreen", width=2
            )

    def draw_pacman(self):
        """Отрисовка Пакмена с анимацией рта"""
        self.canvas.delete("pacman")
        self.canvas.create_oval(
            self.pacman_x * CELL_SIZE + 3,
            self.pacman_y * CELL_SIZE + 3,
            (self.pacman_x + 1) * CELL_SIZE - 3,
            (self.pacman_y + 1) * CELL_SIZE - 3,
            fill=PACMAN_COLOR, tags="pacman"
        )

    def draw_ghosts(self):
        """Отрисовка призраков"""
        self.canvas.delete("ghost")
        for g in self.ghosts:
            color = "blue" if g["vulnerable"] else g["color"]
            self.canvas.create_rectangle(
                g["x"] * CELL_SIZE + 3,
                g["y"] * CELL_SIZE + 3,
                (g["x"] + 1) * CELL_SIZE - 3,
                (g["y"] + 1) * CELL_SIZE - 6,
                fill=color, tags="ghost"
            )
            # Глаза
            self.canvas.create_oval(
                g["x"] * CELL_SIZE + 7, g["y"] * CELL_SIZE + 8,
                g["x"] * CELL_SIZE + 11, g["y"] * CELL_SIZE + 12,
                fill="white", tags="ghost"
            )
            self.canvas.create_oval(
                g["x"] * CELL_SIZE + 16, g["y"] * CELL_SIZE + 8,
                g["x"] * CELL_SIZE + 20, g["y"] * CELL_SIZE + 12,
                fill="white", tags="ghost"
            )

    def update_display(self):
        """Обновление интерфейса"""
        self.score_label.config(text=f"Счёт: {self.score}")
        hearts = "❤️" * self.lives if self.lives > 0 else "💀"
        self.lives_label.config(text=f"Жизни: {hearts}")
        self.level_label.config(text=f"Уровень: {self.current_level}")

    def check_dot(self):
        """Проверка сбора точек"""
        x, y = self.pacman_x, self.pacman_y
        if self.dots[y][x] == 1:
            self.dots[y][x] = 0
            self.canvas.delete(f"dot_{x}_{y}")
            self.score += 10
            self.update_display()
        elif self.dots[y][x] == 2:
            self.dots[y][x] = 0
            self.canvas.delete(f"energizer_{x}_{y}")
            self.score += 50
            self.energizer_active = True
            for g in self.ghosts:
                if not g["in_house"]:
                    g["vulnerable"] = True
                    g["vulnerable_timer"] = 100
            self.update_display()

    def move_pacman(self):
        """Движение Пакмена с телепортами"""
        x, y = self.pacman_x, self.pacman_y

        # Телепорты
        if y == self.height // 2:
            if x < 0:
                self.pacman_x = self.width - 1
                return
            elif x >= self.width:
                self.pacman_x = 0
                return

        dx, dy = self.pacman_next_dir
        nx, ny = x + dx, y + dy

        if 0 <= nx < self.width and 0 <= ny < self.height:
            if self.maze[ny][nx] != 1:
                self.pacman_dir = (dx, dy)
                self.pacman_x, self.pacman_y = nx, ny
                self.check_dot()
                self.draw_pacman()
                return

        dx, dy = self.pacman_dir
        nx, ny = x + dx, y + dy

        if 0 <= nx < self.width and 0 <= ny < self.height:
            if self.maze[ny][nx] != 1:
                self.pacman_x, self.pacman_y = nx, ny
                self.check_dot()
                self.draw_pacman()

    def move_ghosts(self):
        """Движение призраков"""
        for g in self.ghosts:
            if g["in_house"]:
                g["exit_timer"] -= 1
                if g["exit_timer"] <= 0:
                    g["in_house"] = False
                    g["x"] = self.house_exit_x
                    g["y"] = self.house_exit_y
                continue

            if g["vulnerable"]:
                g["vulnerable_timer"] -= 1
                if g["vulnerable_timer"] <= 0:
                    g["vulnerable"] = False
                # Уязвимые призраки убегают случайно
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                random.shuffle(directions)
                moved = False
                for dx, dy in directions:
                    nx, ny = g["x"] + dx, g["y"] + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                        g["x"], g["y"] = nx, ny
                        moved = True
                        break
                if not moved:
                    continue
            else:
                px, py = self.pacman_x, self.pacman_y
                gx, gy = g["x"], g["y"]

                if abs(gx - px) > abs(gy - py):
                    if gx < px:
                        dx, dy = 1, 0
                    else:
                        dx, dy = -1, 0
                else:
                    if gy < py:
                        dx, dy = 0, 1
                    else:
                        dx, dy = 0, -1

                nx, ny = gx + dx, gy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                    g["x"], g["y"] = nx, ny
                else:
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    random.shuffle(directions)
                    for dx, dy in directions:
                        nx, ny = gx + dx, gy + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                            g["x"], g["y"] = nx, ny
                            break

        self.draw_ghosts()

    def check_collision(self):
        """Проверка столкновений"""
        for g in self.ghosts:
            if not g["in_house"] and self.pacman_x == g["x"] and self.pacman_y == g["y"]:
                if g["vulnerable"]:
                    self.score += 200
                    g["in_house"] = True
                    g["exit_timer"] = 50
                    g["vulnerable"] = False
                    g["x"] = g["start_x"]
                    g["y"] = g["start_y"]
                    self.update_display()
                else:
                    self.lives -= 1
                    self.update_display()
                    self.reset_positions()
                    if self.lives <= 0:
                        self.game_over = True
                        self.show_game_over()
                    return

    def reset_positions(self):
        """Сброс позиций"""
        self.pacman_x, self.pacman_y = self.pacman_start_x, self.pacman_start_y
        self.pacman_dir = (0, 0)
        self.pacman_next_dir = (0, 0)
        for g in self.ghosts:
            g["x"] = g["start_x"]
            g["y"] = g["start_y"]
            g["in_house"] = True
            g["vulnerable"] = False
            g["exit_timer"] = 50
        self.energizer_active = False
        self.draw_pacman()
        self.draw_ghosts()

    def check_win(self):
        """Проверка победы"""
        for y in range(self.height):
            for x in range(self.width):
                if self.dots[y][x] in (1, 2):
                    return False
        return True

    def next_level(self):
        """Следующий уровень"""
        self.current_level += 1
        if self.current_level > 3:
            self.win = True
            self.show_game_over()
            return

        self.load_level()
        self.canvas.delete("all")
        self.draw_maze()
        self.draw_pacman()
        self.draw_ghosts()
        self.update_display()

    def game_loop(self):
        """Игровой цикл"""
        if self.game_over or self.win:
            self.root.after(self.game_speed, self.game_loop)
            return

        if not self.paused:
            if self.energizer_active:
                active = any(g["vulnerable"] for g in self.ghosts)
                if not active:
                    self.energizer_active = False

            self.move_pacman()
            self.move_ghosts()
            self.check_collision()

            if self.check_win():
                self.next_level()

        self.root.after(self.game_speed, self.game_loop)

    def key_press(self, event):
        """Обработка клавиш"""
        if self.game_over or self.win:
            if event.keysym == "r" or event.keysym == "R":
                self.restart_game()
            return

        key = event.keysym
        if key == "Up":
            self.pacman_next_dir = (0, -1)
        elif key == "Down":
            self.pacman_next_dir = (0, 1)
        elif key == "Left":
            self.pacman_next_dir = (-1, 0)
        elif key == "Right":
            self.pacman_next_dir = (1, 0)
        elif key == "r" or key == "R":
            self.restart_game()

    def toggle_pause(self, event=None):
        """Пауза"""
        if not self.game_over and not self.win:
            self.paused = not self.paused
            if self.paused:
                self.canvas.create_text(self.width * CELL_SIZE // 2,
                                        self.height * CELL_SIZE // 2,
                                        text="ПАУЗА", fill="white",
                                        font=("Arial", 32, "bold"), tags="pause")
            else:
                self.canvas.delete("pause")

    def show_settings_window(self):
        """Окно настроек"""
        settings_window = Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("350x250")
        settings_window.configure(bg=BG_COLOR)
        settings_window.transient(self.root)
        settings_window.grab_set()

        Label(settings_window, text="⚙ НАСТРОЙКИ", font=("Arial", 16, "bold"),
              fg="gold", bg=BG_COLOR).pack(pady=10)

        Label(settings_window, text="Скорость игры:", font=("Arial", 12),
              fg="white", bg=BG_COLOR).pack(pady=5)

        speed_slider = Scale(settings_window, from_=50, to=250, orient=tk.HORIZONTAL,
                             length=250, bg=BG_COLOR, fg="white",
                             highlightbackground=BG_COLOR)
        speed_slider.set(self.game_speed)
        speed_slider.pack(pady=5)

        speed_label = Label(settings_window, text=f"Задержка: {self.game_speed} мс",
                            font=("Arial", 10), fg="gray", bg=BG_COLOR)
        speed_label.pack(pady=5)

        def update_label(val):
            speed_label.config(text=f"Задержка: {int(float(val))} мс")
        speed_slider.config(command=update_label)

        def save_speed():
            self.game_speed = int(speed_slider.get())
            self.settings["game_speed"] = self.game_speed
            self.save_settings()
            settings_window.destroy()
            messagebox.showinfo("Настройки", "Скорость сохранена!")

        Button(settings_window, text="Сохранить", command=save_speed,
               bg="green", fg="white", font=("Arial", 12)).pack(pady=15)

    def show_records_window(self):
        """Окно рекордов"""
        records_window = Toplevel(self.root)
        records_window.title("Рекорды")
        records_window.geometry("400x400")
        records_window.configure(bg=BG_COLOR)
        records_window.transient(self.root)

        Label(records_window, text="🏆 ТАБЛИЦА РЕКОРДОВ 🏆",
              font=("Arial", 16, "bold"), fg="gold", bg=BG_COLOR).pack(pady=10)

        header = Frame(records_window, bg=BG_COLOR)
        header.pack(fill=tk.X, padx=20, pady=5)
        Label(header, text="№", width=5, font=("Arial", 12, "bold"),
              fg="white", bg=BG_COLOR).pack(side=tk.LEFT)
        Label(header, text="Игрок", width=20, font=("Arial", 12, "bold"),
              fg="white", bg=BG_COLOR).pack(side=tk.LEFT)
        Label(header, text="Счёт", width=10, font=("Arial", 12, "bold"),
              fg="white", bg=BG_COLOR).pack(side=tk.LEFT)

        Frame(records_window, height=2, bg="gray").pack(fill=tk.X, padx=20, pady=5)

        records_frame = Frame(records_window, bg=BG_COLOR)
        records_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        if self.scores:
            for i, record in enumerate(self.scores[:10], 1):
                row = Frame(records_frame, bg=BG_COLOR)
                row.pack(fill=tk.X, pady=2)
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
                Label(row, text=medal, width=5, font=("Arial", 12),
                      fg="yellow" if i <= 3 else "white", bg=BG_COLOR).pack(side=tk.LEFT)
                Label(row, text=record["name"], width=20, font=("Arial", 12),
                      fg="white", bg=BG_COLOR, anchor="w").pack(side=tk.LEFT)
                Label(row, text=str(record["score"]), width=10, font=("Arial", 12),
                      fg="yellow", bg=BG_COLOR).pack(side=tk.LEFT)
        else:
            Label(records_frame, text="Пока нет рекордов", font=("Arial", 12),
                  fg="gray", bg=BG_COLOR).pack(pady=50)

        Button(records_window, text="Закрыть", command=records_window.destroy,
               bg="red", fg="white", font=("Arial", 12)).pack(pady=10)

    def show_start_menu(self):
        """Стартовое меню с 4 кнопками"""
        self.canvas.delete("all")

        # Заголовок
        self.canvas.create_text(self.width * CELL_SIZE // 2,
                                self.height * CELL_SIZE // 2 - 100,
                                text="ПАКМЕН", fill="yellow",
                                font=("Arial", 52, "bold"))

        # Кнопка СТАРТ
        self.start_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 - 30,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 10,
            fill="green", outline="white", width=3
        )
        self.start_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 - 10,
            text="СТАРТ", fill="white", font=("Arial", 20, "bold")
        )

        # Кнопка НАСТРОЙКИ
        self.settings_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 + 20,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 60,
            fill="gray", outline="white", width=3
        )
        self.settings_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 40,
            text="НАСТРОЙКИ", fill="white", font=("Arial", 20, "bold")
        )

        # Кнопка РЕКОРДЫ
        self.records_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 + 70,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 110,
            fill="blue", outline="white", width=3
        )
        self.records_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 90,
            text="РЕКОРДЫ", fill="white", font=("Arial", 20, "bold")
        )

        # Кнопка ВЫХОД
        self.exit_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 + 120,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 160,
            fill="red", outline="white", width=3
        )
        self.exit_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 140,
            text="ВЫХОД", fill="white", font=("Arial", 20, "bold")
        )

        # Привязка событий
        self.canvas.tag_bind(self.start_btn, "<Button-1>", self.start_game)
        self.canvas.tag_bind(self.start_text, "<Button-1>", self.start_game)
        self.canvas.tag_bind(self.settings_btn, "<Button-1>", lambda e: self.show_settings_window())
        self.canvas.tag_bind(self.settings_text, "<Button-1>", lambda e: self.show_settings_window())
        self.canvas.tag_bind(self.records_btn, "<Button-1>", lambda e: self.show_records_window())
        self.canvas.tag_bind(self.records_text, "<Button-1>", lambda e: self.show_records_window())
        self.canvas.tag_bind(self.exit_btn, "<Button-1>", self.exit_game)
        self.canvas.tag_bind(self.exit_text, "<Button-1>", self.exit_game)

    def start_game(self, event=None):
        """Начало игры"""
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False

        self.load_level()
        self.canvas.delete("all")
        self.draw_maze()
        self.draw_pacman()
        self.draw_ghosts()
        self.update_display()
        self.game_loop()

    def show_game_over(self):
        """Конец игры"""
        self.canvas.delete("all")

        # Запрос имени при рекорде
        if self.score > 0 and (not self.scores or self.score > self.scores[-1]["score"] if self.scores else True):
            self.ask_for_name()
        else:
            text = "ПОБЕДА!" if self.win else "ИГРА ОКОНЧЕНА"
            color = "green" if self.win else "red"

            self.canvas.create_text(self.width * CELL_SIZE // 2,
                                    self.height * CELL_SIZE // 2 - 30,
                                    text=text, fill=color,
                                    font=("Arial", 32, "bold"))
            self.canvas.create_text(self.width * CELL_SIZE // 2,
                                    self.height * CELL_SIZE // 2 + 20,
                                    text=f"Счёт: {self.score}",
                                    fill="white", font=("Arial", 20))
            self.canvas.create_text(self.width * CELL_SIZE // 2,
                                    self.height * CELL_SIZE // 2 + 80,
                                    text="Нажмите R для перезапуска",
                                    fill="gray", font=("Arial", 14))

    def ask_for_name(self):
        """Запрос имени для рекорда"""
        dialog = Toplevel(self.root)
        dialog.title("Новый рекорд!")
        dialog.geometry("300x150")
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()

        Label(dialog, text=f"Ваш счёт: {self.score}",
              font=("Arial", 14), fg="yellow", bg=BG_COLOR).pack(pady=10)
        Label(dialog, text="Введите имя:", font=("Arial", 12),
              fg="white", bg=BG_COLOR).pack()

        entry = tk.Entry(dialog, font=("Arial", 12))
        entry.pack(pady=5)
        entry.insert(0, "Игрок")

        def save():
            name = entry.get().strip()
            if not name:
                name = "Игрок"
            self.add_score(name, self.score)
            dialog.destroy()
            self.show_game_over()

        Button(dialog, text="Сохранить", command=save,
               bg="green", fg="white", font=("Arial", 12)).pack(pady=10)
        entry.bind("<Return>", lambda e: save())

    def restart_game(self):
        """Перезапуск игры"""
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False

        self.load_level()
        self.canvas.delete("all")
        self.show_start_menu()

    def exit_game(self, event=None):
        """Выход из игры"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = PacmanGame(root)
    root.mainloop()