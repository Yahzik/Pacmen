# game.py
import tkinter as tk
from tkinter import messagebox, Toplevel, Scale, Label, Button, Frame
import json
import os
from config import *
from ghosts import Ghost, GhostManager


class PacmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("ПАКМЕН")
        self.root.configure(bg=BG_COLOR)

        self.load_settings()
        self.scores = self.load_scores()

        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False
        self.game_speed = self.settings.get("game_speed", DEFAULT_GAME_SPEED)
        self.after_id = None

        self.pacman_x = 0
        self.pacman_y = 0
        self.pacman_start_x = 0
        self.pacman_start_y = 0
        self.pacman_dir = (0, 0)
        self.pacman_next_dir = (0, 0)

        self.ghost_manager = None

        self.maze = []
        self.dots = []
        self.width = 0
        self.height = 0

        self.load_level()
        self.create_widgets()

        self.root.bind("<Key>", self.key_press)
        self.root.bind("<p>", self.toggle_pause)
        self.root.bind("<P>", self.toggle_pause)
        self.root.bind("<Escape>", self.exit_game)

        self.top_frame.pack_forget()
        self.show_start_menu()

    def load_settings(self):
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
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def load_scores(self):
        if os.path.exists(RECORDS_FILE):
            try:
                with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("scores", [])
            except:
                return []
        return []

    def save_scores(self):
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]
        with open(RECORDS_FILE, "w", encoding="utf-8") as f:
            json.dump({"scores": self.scores}, f, ensure_ascii=False, indent=2)

    def add_score(self, player_name, score):
        self.scores.append({"name": player_name, "score": score})
        self.save_scores()

    def load_level(self):
        filename = MAZE_FILE if self.current_level == 1 else f"level_{self.current_level}.txt"

        if not os.path.exists(filename):
            filename = MAZE_FILE

        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        self.height = len(lines)
        self.width = len(lines[0])

        self.maze = []
        self.dots = []
        ghost_list = []

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
                    ghost_list.append((x, y, 0))
                elif ch == 'K':
                    row.append(0)
                    dot_row.append(0)
                    ghost_list.append((x, y, 1))
                elif ch == 'I':
                    row.append(0)
                    dot_row.append(0)
                    ghost_list.append((x, y, 2))
                elif ch == 'C':
                    row.append(0)
                    dot_row.append(0)
                    ghost_list.append((x, y, 3))
                else:
                    row.append(0)
                    dot_row.append(0)
            self.maze.append(row)
            self.dots.append(dot_row)

        ghosts = []
        for i, (x, y, t) in enumerate(ghost_list):
            ghost = Ghost(self.house_center_x, self.house_center_y, t, GHOST_COLORS[t])
            ghost.exit_timer = 30 + i * 20
            ghosts.append(ghost)

        self.ghost_manager = GhostManager(ghosts, self.maze, self.width, self.height,
                                          self.house_exit_x, self.house_exit_y)

        self.update_window()

    def update_window(self):
        width = self.width * CELL_SIZE + 20
        height = self.height * CELL_SIZE + 100
        self.root.geometry(f"{width}x{height}")

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root, bg=BG_COLOR)

        self.score_label = tk.Label(self.top_frame, text=f"Счёт: 0", font=("Arial", 14, "bold"),
                                    fg="white", bg=BG_COLOR)
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.lives_label = tk.Label(self.top_frame, text="Жизни: ❤️❤️❤️", font=("Arial", 14),
                                    fg="red", bg=BG_COLOR)
        self.lives_label.pack(side=tk.LEFT, padx=20)

        self.level_label = tk.Label(self.top_frame, text="Уровень: 1", font=("Arial", 14, "bold"),
                                    fg="white", bg=BG_COLOR)
        self.level_label.pack(side=tk.LEFT, padx=20)

        self.canvas = tk.Canvas(self.root, width=self.width * CELL_SIZE,
                                height=self.height * CELL_SIZE, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack()

        bottom = tk.Frame(self.root, bg=BG_COLOR)
        bottom.pack(pady=10)

        tk.Label(bottom, text="Управление: ← ↑ ↓ → | P - Пауза | ESC - Выход",
                 font=("Arial", 10), fg="gray", bg=BG_COLOR).pack()

    def draw_maze(self):
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

    def draw_pacman(self):
        self.canvas.delete("pacman")
        self.canvas.create_oval(
            self.pacman_x * CELL_SIZE + 3,
            self.pacman_y * CELL_SIZE + 3,
            (self.pacman_x + 1) * CELL_SIZE - 3,
            (self.pacman_y + 1) * CELL_SIZE - 3,
            fill=PACMAN_COLOR, tags="pacman"
        )

    def draw_ghosts(self):
        self.canvas.delete("ghost")
        for g in self.ghost_manager.get_ghosts():
            color = "blue" if g.vulnerable else g.color
            self.canvas.create_rectangle(
                g.x * CELL_SIZE + 3,
                g.y * CELL_SIZE + 3,
                (g.x + 1) * CELL_SIZE - 3,
                (g.y + 1) * CELL_SIZE - 6,
                fill=color, tags="ghost"
            )
            self.canvas.create_oval(
                g.x * CELL_SIZE + 7, g.y * CELL_SIZE + 8,
                g.x * CELL_SIZE + 11, g.y * CELL_SIZE + 12,
                fill="white", tags="ghost"
            )
            self.canvas.create_oval(
                g.x * CELL_SIZE + 16, g.y * CELL_SIZE + 8,
                g.x * CELL_SIZE + 20, g.y * CELL_SIZE + 12,
                fill="white", tags="ghost"
            )

    def update_display(self):
        self.score_label.config(text=f"Счёт: {self.score}")
        hearts = "❤️" * self.lives if self.lives > 0 else "💀"
        self.lives_label.config(text=f"Жизни: {hearts}")
        self.level_label.config(text=f"Уровень: {self.current_level}")

    def check_dot(self):
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
            self.ghost_manager.make_vulnerable()
            self.update_display()

    def move_pacman(self):
        x, y = self.pacman_x, self.pacman_y

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

    def check_collision(self):
        for g in self.ghost_manager.get_ghosts():
            if not g.in_house and self.pacman_x == g.x and self.pacman_y == g.y:
                if g.vulnerable:
                    self.score += 200
                    g.in_house = True
                    g.exit_timer = 50
                    g.vulnerable = False
                    g.x = g.start_x
                    g.y = g.start_y
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
        self.pacman_x, self.pacman_y = self.pacman_start_x, self.pacman_start_y
        self.pacman_dir = (0, 0)
        self.pacman_next_dir = (0, 0)
        self.ghost_manager.reset_positions()
        self.energizer_active = False
        self.draw_pacman()
        self.draw_ghosts()

    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.dots[y][x] in (1, 2):
                    return False
        return True

    def next_level(self):
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

    # ==================== ИГРОВОЙ ЦИКЛ ====================
    def game_update(self):
        """Один шаг игры (движение, коллизии, проверка победы)"""
        if self.game_over or self.win:
            return

        if self.energizer_active:
            if not self.ghost_manager.check_vulnerable_active():
                self.energizer_active = False

        self.move_pacman()
        self.ghost_manager.move_ghosts(self.pacman_x, self.pacman_y, self.pacman_dir)
        self.draw_ghosts()
        self.check_collision()

        if self.check_win():
            self.next_level()

    def start_game_loop(self):
        """Запускает игровой цикл"""
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
        self._game_loop()

    def _game_loop(self):
        """Игровой цикл (вызывается каждые game_speed мс)"""
        # Игровая логика выполняется только если пауза ВЫКЛЮЧЕНА и игра не окончена
        if not self.game_over and not self.win and not self.paused:
            self.game_update()

        # Запускаем следующий кадр ВСЕГДА (даже на паузе)
        self.after_id = self.root.after(self.game_speed, self._game_loop)

    def stop_game_loop(self):
        """Останавливает игровой цикл"""
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def toggle_pause(self, event=None):
        """Переключение паузы (работает 100%)"""
        if self.game_over or self.win:
            return

        # Переключаем флаг паузы
        self.paused = not self.paused

        if self.paused:
            # Показываем текст паузы
            self.pause_text = self.canvas.create_text(
                self.width * CELL_SIZE // 2,
                self.height * CELL_SIZE // 2,
                text="ПАУЗА\nНажмите P для продолжения",
                fill="yellow", font=("Arial", 32, "bold"),
                justify="center"
            )
            print("=== ПАУЗА ВКЛЮЧЕНА ===")
        else:
            # Убираем текст паузы
            if hasattr(self, 'pause_text'):
                self.canvas.delete(self.pause_text)
            print("=== ПАУЗА ВЫКЛЮЧЕНА ===")

    # ==================== GUI ====================
    def key_press(self, event):
        if self.game_over or self.win:
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

    def show_settings_window(self):
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
            new_speed = int(speed_slider.get())
            self.game_speed = new_speed
            self.settings["game_speed"] = new_speed
            self.save_settings()
            settings_window.destroy()
            messagebox.showinfo("Настройки", "Скорость сохранена!")

        Button(settings_window, text="Сохранить", command=save_speed,
               bg="green", fg="white", font=("Arial", 12)).pack(pady=15)

    def show_records_window(self):
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
        self.canvas.delete("all")

        self.canvas.create_text(self.width * CELL_SIZE // 2,
                                self.height * CELL_SIZE // 2 - 80,
                                text="ПАКМЕН", fill="yellow",
                                font=("Arial", 52, "bold"))

        self.start_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 - 20,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 20,
            fill="green", outline="white", width=3
        )
        self.start_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2,
            text="СТАРТ", fill="white", font=("Arial", 20, "bold")
        )

        self.settings_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 + 40,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 80,
            fill="gray", outline="white", width=3
        )
        self.settings_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 60,
            text="НАСТРОЙКИ", fill="white", font=("Arial", 20, "bold")
        )

        self.records_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 + 100,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 140,
            fill="blue", outline="white", width=3
        )
        self.records_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 120,
            text="РЕКОРДЫ", fill="white", font=("Arial", 20, "bold")
        )

        self.exit_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 100, self.height * CELL_SIZE // 2 + 160,
            self.width * CELL_SIZE // 2 + 100, self.height * CELL_SIZE // 2 + 200,
            fill="red", outline="white", width=3
        )
        self.exit_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 180,
            text="ВЫХОД", fill="white", font=("Arial", 20, "bold")
        )

        self.canvas.create_text(self.width * CELL_SIZE // 2,
                                self.height * CELL_SIZE // 2 + 240,
                                text="Управление: ← ↑ ↓ → | P - Пауза | ESC - Выход",
                                fill="gray", font=("Arial", 10))

        self.canvas.tag_bind(self.start_btn, "<Button-1>", self.start_game)
        self.canvas.tag_bind(self.start_text, "<Button-1>", self.start_game)
        self.canvas.tag_bind(self.settings_btn, "<Button-1>", lambda e: self.show_settings_window())
        self.canvas.tag_bind(self.settings_text, "<Button-1>", lambda e: self.show_settings_window())
        self.canvas.tag_bind(self.records_btn, "<Button-1>", lambda e: self.show_records_window())
        self.canvas.tag_bind(self.records_text, "<Button-1>", lambda e: self.show_records_window())
        self.canvas.tag_bind(self.exit_btn, "<Button-1>", self.exit_game)
        self.canvas.tag_bind(self.exit_text, "<Button-1>", self.exit_game)

    def start_game(self, event=None):
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.game_over = False
        self.win = False
        self.paused = False
        self.energizer_active = False

        self.top_frame.pack(pady=10)

        self.load_level()
        self.canvas.delete("all")
        self.draw_maze()
        self.draw_pacman()
        self.draw_ghosts()
        self.update_display()

        self.start_game_loop()

    def show_game_over(self):
        self.stop_game_loop()
        self.canvas.delete("all")
        self.top_frame.pack_forget()

        if self.win:
            title = "ПОБЕДА!"
            title_color = "green"
            message = "Вы прошли все уровни!"
        else:
            title = "ПОРАЖЕНИЕ"
            title_color = "red"
            message = "Игра окончена"

        self.canvas.create_text(self.width * CELL_SIZE // 2,
                                self.height * CELL_SIZE // 2 - 60,
                                text=title, fill=title_color,
                                font=("Arial", 40, "bold"))

        self.canvas.create_text(self.width * CELL_SIZE // 2,
                                self.height * CELL_SIZE // 2 - 10,
                                text=message, fill="white",
                                font=("Arial", 16))

        self.canvas.create_text(self.width * CELL_SIZE // 2,
                                self.height * CELL_SIZE // 2 + 30,
                                text=f"Счёт: {self.score}", fill="yellow",
                                font=("Arial", 24, "bold"))

        self.restart_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 80, self.height * CELL_SIZE // 2 + 90,
            self.width * CELL_SIZE // 2 + 80, self.height * CELL_SIZE // 2 + 130,
            fill="green", outline="white", width=2
        )
        self.restart_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 110,
            text="ЗАНОВО", fill="white", font=("Arial", 16, "bold")
        )

        self.menu_btn = self.canvas.create_rectangle(
            self.width * CELL_SIZE // 2 - 80, self.height * CELL_SIZE // 2 + 140,
            self.width * CELL_SIZE // 2 + 80, self.height * CELL_SIZE // 2 + 180,
            fill="blue", outline="white", width=2
        )
        self.menu_text = self.canvas.create_text(
            self.width * CELL_SIZE // 2, self.height * CELL_SIZE // 2 + 160,
            text="ГЛАВНОЕ МЕНЮ", fill="white", font=("Arial", 16, "bold")
        )

        self.canvas.tag_bind(self.restart_btn, "<Button-1>", lambda e: self.restart_game())
        self.canvas.tag_bind(self.restart_text, "<Button-1>", lambda e: self.restart_game())
        self.canvas.tag_bind(self.menu_btn, "<Button-1>", lambda e: self.back_to_menu())
        self.canvas.tag_bind(self.menu_text, "<Button-1>", lambda e: self.back_to_menu())

    def back_to_menu(self):
        self.stop_game_loop()
        self.game_over = False
        self.win = False
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.show_start_menu()

    def restart_game(self):
        self.stop_game_loop()
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
        self.stop_game_loop()
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = PacmanGame(root)
    root.mainloop()