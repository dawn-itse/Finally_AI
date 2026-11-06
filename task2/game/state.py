from game.entities import (
    ACTION_TO_DIRECTION,
    DIRECTION_DELTAS,
    Base,
    Bullet,
    Tank,
    Wall,
)


class GameState:
    def __init__(self, width: int = 9, height: int = 9, max_turns: int = 200):
        self.width = width
        self.height = height
        self.max_turns = max_turns
        self.turn_count = 0
        self.current_player = 1

        self.tanks = {}
        self.bases = {}
        self.walls = {}
        self.bullets = []

    def clone(self):
        new_state = GameState(self.width, self.height, self.max_turns)
        new_state.turn_count = self.turn_count
        new_state.current_player = self.current_player
        new_state.tanks = {pid: tank.clone() for pid, tank in self.tanks.items()}
        new_state.bases = {pid: base.clone() for pid, base in self.bases.items()}
        new_state.walls = {pos: wall.clone() for pos, wall in self.walls.items()}
        new_state.bullets = [b.clone() for b in self.bullets]
        return new_state

    @classmethod
    def create_default_map(cls, width: int = 9, height: int = 9):
        state = cls(width, height)
        mid_x = width // 2

        # Player 1 (Bottom side, facing UP)
        state.bases[1] = Base(mid_x, height - 1, player_id=1)
        state.tanks[1] = Tank(mid_x, height - 2, direction="UP", player_id=1)

        # Player 2 (Top side, facing DOWN)
        state.bases[2] = Base(mid_x, 0, player_id=2)
        state.tanks[2] = Tank(mid_x, 1, direction="DOWN", player_id=2)

        # Symmetric walls on the battlefield
        wall_positions = [
            (mid_x - 1, height - 2),
            (mid_x + 1, height - 2),
            (mid_x - 1, 1),
            (mid_x + 1, 1),
            (mid_x - 2, height // 2),
            (mid_x, height // 2),
            (mid_x + 2, height // 2),
            (1, height // 2 - 1),
            (width - 2, height // 2 - 1),
            (1, height // 2 + 1),
            (width - 2, height // 2 + 1),
        ]
        for wx, wy in wall_positions:
            if 0 <= wx < width and 0 <= wy < height:
                if (wx, wy) not in [(mid_x, height - 1), (mid_x, height - 2), (mid_x, 0), (mid_x, 1)]:
                    state.walls[(wx, wy)] = Wall(wx, wy)

        return state

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_cell_blocked(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return True
        if (x, y) in self.walls and self.walls[(x, y)].is_alive():
            return True
        for base in self.bases.values():
            if base.is_alive() and base.x == x and base.y == y:
                return True
        for tank in self.tanks.values():
            if tank.is_alive() and tank.x == x and tank.y == y:
                return True
        return False

    # ACTIONS(s) in Lecture 07
    def get_legal_actions(self, player_id: int = None) -> list:
        if player_id is None:
            player_id = self.current_player
        tank = self.tanks.get(player_id)
        if tank is None or not tank.is_alive():
            return ["STAY"]

        legal = ["FIRE", "STAY"]
        for action, direction in ACTION_TO_DIRECTION.items():
            dx, dy = DIRECTION_DELTAS[direction]
            nx, ny = tank.x + dx, tank.y + dy
            if not self.is_cell_blocked(nx, ny):
                legal.append(action)
        return legal

    # RESULT(s, a) in Lecture 07 (returns a new state without modifying current state)
    def get_next_state(self, action: str):
        next_state = self.clone()
        next_state.apply_action(action)
        return next_state

    def apply_action(self, action: str):
        player_id = self.current_player
        tank = self.tanks.get(player_id)

        if tank is not None and tank.is_alive():
            if action in ACTION_TO_DIRECTION:
                new_dir = ACTION_TO_DIRECTION[action]
                tank.direction = new_dir
                dx, dy = DIRECTION_DELTAS[new_dir]
                nx, ny = tank.x + dx, tank.y + dy
                if not self.is_cell_blocked(nx, ny):
                    tank.x = nx
                    tank.y = ny
            elif action == "FIRE":
                bullet = Bullet(tank.x, tank.y, tank.direction, owner_id=player_id)
                self.bullets.append(bullet)
            elif action == "STAY":
                pass

        # Update all active bullets (each moves up to 3 cells, checking collision cell by cell)
        self._update_bullets()

        self.turn_count += 1
        self.current_player = 2 if self.current_player == 1 else 1

    def _update_bullets(self):
        remaining_bullets = []
        for bullet in self.bullets:
            if not bullet.active:
                continue

            dx, dy = DIRECTION_DELTAS[bullet.direction]
            for _ in range(Bullet.SPEED):
                bullet.x += dx
                bullet.y += dy

                if not self.is_inside(bullet.x, bullet.y):
                    bullet.active = False
                    break

                if self._check_bullet_collision(bullet):
                    bullet.active = False
                    break

            if bullet.active:
                remaining_bullets.append(bullet)

        self.bullets = remaining_bullets

    def _check_bullet_collision(self, bullet: Bullet) -> bool:
        pos = (bullet.x, bullet.y)

        # 1. Check wall collision
        if pos in self.walls and self.walls[pos].is_alive():
            self.walls[pos].take_damage(Bullet.DAMAGE)
            if not self.walls[pos].is_alive():
                del self.walls[pos]
            return True

        # 2. Check tank collision
        for pid, tank in self.tanks.items():
            if tank.is_alive() and tank.x == bullet.x and tank.y == bullet.y:
                tank.take_damage(Bullet.DAMAGE)
                return True

        # 3. Check base collision
        for pid, base in self.bases.items():
            if base.is_alive() and base.x == bullet.x and base.y == bullet.y:
                base.take_damage(Bullet.DAMAGE)
                return True

        return False

    # TERMINAL-TEST(s) in Lecture 07
    def is_terminal(self) -> bool:
        if self.turn_count >= self.max_turns:
            return True
        for pid in (1, 2):
            if not self.tanks[pid].is_alive() or not self.bases[pid].is_alive():
                return True
        return False

    def get_winner(self):
        p1_alive = self.tanks[1].is_alive() and self.bases[1].is_alive()
        p2_alive = self.tanks[2].is_alive() and self.bases[2].is_alive()

        if p1_alive and not p2_alive:
            return 1
        if p2_alive and not p1_alive:
            return 2
        return None

    # UTILITY(s, p) in Lecture 07
    def get_utility(self, player_id: int = 1) -> float:
        winner = self.get_winner()
        if winner == player_id:
            return 1000.0
        elif winner is not None:
            return -1000.0
        return 0.0
