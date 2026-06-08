# ghosts.py
import random


class Ghost:
    def __init__(self, x, y, ghost_type, color):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.type = ghost_type  # 0=Blinky, 1=Pinky, 2=Inky, 3=Clyde
        self.color = color
        self.in_house = True
        self.exit_timer = 0
        self.dir = (1, 0)
        self.vulnerable = False
        self.vulnerable_timer = 0


class GhostManager:
    def __init__(self, ghosts, maze, width, height, house_exit_x, house_exit_y):
        self.ghosts = ghosts
        self.maze = maze
        self.width = width
        self.height = height
        self.house_exit_x = house_exit_x
        self.house_exit_y = house_exit_y
        self.blinky = None
        self.update_blinky()

    def update_blinky(self):
        for g in self.ghosts:
            if g.type == 0:
                self.blinky = g
                break

    def get_blinky(self):
        return self.blinky

    def move_ghosts(self, pacman_x, pacman_y, pacman_dir):
        """Движение всех призраков с правильными алгоритмами"""
        self.update_blinky()

        for g in self.ghosts:
            # ========== ВЫХОД ИЗ ДОМА ==========
            if g.in_house:
                g.exit_timer -= 1
                if g.exit_timer <= 0:
                    g.in_house = False
                    g.x = self.house_exit_x
                    g.y = self.house_exit_y
                continue

            # ========== УЯЗВИМЫЕ ПРИЗРАКИ (убегают) ==========
            if g.vulnerable:
                g.vulnerable_timer -= 1
                if g.vulnerable_timer <= 0:
                    g.vulnerable = False

                # Убегают от Пакмена
                best_dx, best_dy = 0, 0
                max_dist = -1

                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = g.x + dx, g.y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                        dist = (nx - pacman_x) ** 2 + (ny - pacman_y) ** 2
                        if dist > max_dist:
                            max_dist = dist
                            best_dx, best_dy = dx, dy

                if best_dx != 0 or best_dy != 0:
                    g.x += best_dx
                    g.y += best_dy
                continue

            # ========== АЛГОРИТМЫ ПРИЗРАКОВ ==========
            target_x, target_y = self._get_target(g, pacman_x, pacman_y, pacman_dir)

            # ========== ВЫБОР НАПРАВЛЕНИЯ К ЦЕЛИ ==========
            self._move_towards_target(g, target_x, target_y)

    def _get_target(self, ghost, pacman_x, pacman_y, pacman_dir):
        """Определение цели в зависимости от типа призрака"""
        if ghost.type == 0:  # Блинки - прямой преследователь
            return pacman_x, pacman_y

        elif ghost.type == 1:  # Пинки - засада (4 клетки вперёд)
            dx, dy = pacman_dir
            target_x = pacman_x + dx * 4
            target_y = pacman_y + dy * 4
            if dy == -1:
                target_x = pacman_x - 4
            target_x = max(0, min(target_x, self.width - 1))
            target_y = max(0, min(target_y, self.height - 1))
            return target_x, target_y

        elif ghost.type == 2:  # Инки - комбинированный (от Блинки)
            if self.blinky:
                vec_x = pacman_x - self.blinky.x
                vec_y = pacman_y - self.blinky.y
                target_x = pacman_x + vec_x * 2
                target_y = pacman_y + vec_y * 2
                target_x = max(0, min(target_x, self.width - 1))
                target_y = max(0, min(target_y, self.height - 1))
                return target_x, target_y
            return pacman_x, pacman_y

        else:  # ghost.type == 3 - Клайд (трусливый)
            dist = ((ghost.x - pacman_x) ** 2 + (ghost.y - pacman_y) ** 2) ** 0.5
            if dist > 8:
                return pacman_x, pacman_y
            else:
                # Случайное движение
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                random.shuffle(directions)
                for dx, dy in directions:
                    nx, ny = ghost.x + dx, ghost.y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                        ghost.x, ghost.y = nx, ny
                        return ghost.x, ghost.y
                return pacman_x, pacman_y

    def _move_towards_target(self, ghost, target_x, target_y):
        """Движение призрака к цели"""
        best_dx, best_dy = 0, 0
        min_dist = float('inf')

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = ghost.x + dx, ghost.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                # Не разворачиваемся назад
                if (dx, dy) == (-ghost.dir[0], -ghost.dir[1]):
                    continue
                dist = (nx - target_x) ** 2 + (ny - target_y) ** 2
                if dist < min_dist:
                    min_dist = dist
                    best_dx, best_dy = dx, dy

        if best_dx != 0 or best_dy != 0:
            ghost.x += best_dx
            ghost.y += best_dy
            ghost.dir = (best_dx, best_dy)
        else:
            # Запасной вариант
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = ghost.x + dx, ghost.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] != 1:
                    ghost.x, ghost.y = nx, ny
                    ghost.dir = (dx, dy)
                    break

    def make_vulnerable(self):
        """Сделать всех призраков уязвимыми"""
        for g in self.ghosts:
            if not g.in_house:
                g.vulnerable = True
                g.vulnerable_timer = 100

    def check_vulnerable_active(self):
        """Проверить, есть ли уязвимые призраки"""
        return any(g.vulnerable for g in self.ghosts)

    def get_ghosts(self):
        return self.ghosts

    def reset_positions(self):
        """Сброс позиций призраков"""
        for g in self.ghosts:
            g.x = g.start_x
            g.y = g.start_y
            g.in_house = True
            g.vulnerable = False
            g.exit_timer = 50