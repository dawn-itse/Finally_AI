import math
import pygame
from agents.base_agent import BaseAgent, RandomAgent, load_external_agent
from agents.minimax_agent import MinimaxAgent
from game.entities import DIRECTION_DELTAS
from game.state import GameState


class Button:
    def __init__(self, rect: pygame.Rect, label: str, action_id: str, group: str = ""):
        self.rect = rect
        self.label = label
        self.action_id = action_id
        self.group = group


class TankBattleUI:
    CELL_SIZE = 68
    BOARD_PADDING = 20
    PANEL_WIDTH = 420
    FPS = 60

    # Tactical dark arena palette
    COLOR_BG = (15, 19, 26)
    COLOR_FRAME_OUTER = (52, 60, 74)
    COLOR_FRAME_INNER = (30, 36, 46)
    COLOR_BOARD_BG = (18, 22, 28)
    COLOR_TILE_ALT = (22, 27, 35)
    COLOR_GRID = (34, 41, 52)

    COLOR_PANEL = (22, 27, 36)
    COLOR_CARD = (30, 37, 49)
    COLOR_CARD_BORDER = (52, 63, 82)
    COLOR_BTN = (42, 51, 66)
    COLOR_BTN_HOVER = (58, 70, 90)
    COLOR_BTN_TEXT = (232, 238, 246)

    COLOR_TEXT = (240, 244, 250)
    COLOR_SUBTEXT = (158, 170, 188)

    # Player 1 (Blue / Gold accents)
    COLOR_P1_MAIN = (46, 154, 240)
    COLOR_P1_LIGHT = (112, 196, 255)
    COLOR_P1_DARK = (26, 94, 158)
    COLOR_P1_TREAD = (38, 46, 58)

    # Player 2 (Crimson / Amber accents)
    COLOR_P2_MAIN = (235, 77, 75)
    COLOR_P2_LIGHT = (255, 134, 132)
    COLOR_P2_DARK = (158, 38, 38)
    COLOR_P2_TREAD = (48, 38, 42)

    # Brick wall colors (Battle City terracotta style)
    COLOR_MORTAR = (68, 34, 26)
    COLOR_BRICK = (184, 78, 44)
    COLOR_BRICK_HI = (218, 112, 72)
    COLOR_BRICK_SH = (128, 48, 26)

    COLOR_BULLET_CORE = (255, 252, 220)
    COLOR_BULLET_GLOW = (255, 185, 45)
    COLOR_HP_BG = (42, 48, 58)
    COLOR_HP_GREEN = (46, 204, 113)
    COLOR_HP_YELLOW = (241, 196, 15)
    COLOR_HP_RED = (231, 76, 60)

    SPEED_PRESETS = [
        ("Slow", 650),
        ("Normal", 320),
        ("Fast", 140),
        ("Turbo", 45),
    ]

    def __init__(
        self,
        state: GameState = None,
        agent1: BaseAgent = None,
        agent2: BaseAgent = None,
        step_delay_ms: int = 320,
    ):
        self.state = state if state is not None else GameState.create_default_map()
        self.agent1 = (
            agent1
            if agent1 is not None
            else MinimaxAgent(1, depth=3, use_alpha_beta=True, use_heuristic=True)
        )
        self.agent2 = (
            agent2
            if agent2 is not None
            else MinimaxAgent(2, depth=3, use_alpha_beta=True, use_heuristic=False)
        )
        self.step_delay_ms = step_delay_ms
        self.paused = False
        self.human_p1 = False
        self.pending_human_action = None
        self.last_action_text = "Ready"

        self.p1_mode_idx = self._infer_mode_index(self.agent1)
        self.p2_mode_idx = self._infer_mode_index(self.agent2)

        # Visual animation states (purely cosmetic, does not alter GameState)
        self.tank_anims = {}
        self.tread_phases = {1: 0, 2: 0}
        self.recoil_timers = {1: 0, 2: 0}
        self.bullet_tracers = []
        self.explosions = []
        self.particles = []
        self.popups = []
        self.buttons = []

    def _infer_mode_index(self, agent: BaseAgent) -> int:
        if isinstance(agent, MinimaxAgent):
            if not agent.use_heuristic and not agent.use_alpha_beta:
                return 1
            if not agent.use_heuristic and agent.use_alpha_beta:
                return 2
            if agent.use_heuristic and not agent.use_alpha_beta:
                return 3
            return 4
        if isinstance(agent, RandomAgent):
            return 0
        return -1

    def set_agent_mode(self, player_id: int, mode_index: int):
        if mode_index == 1:
            agent = MinimaxAgent(player_id, depth=3, use_alpha_beta=False, use_heuristic=False)
        elif mode_index == 2:
            agent = MinimaxAgent(player_id, depth=3, use_alpha_beta=True, use_heuristic=False)
        elif mode_index == 3:
            agent = MinimaxAgent(player_id, depth=3, use_alpha_beta=False, use_heuristic=True)
        elif mode_index == 4:
            agent = MinimaxAgent(player_id, depth=3, use_alpha_beta=True, use_heuristic=True)
        else:
            agent = RandomAgent(player_id)

        if player_id == 1:
            self.human_p1 = False
            self.agent1 = agent
            self.p1_mode_idx = mode_index
        else:
            self.agent2 = agent
            self.p2_mode_idx = mode_index

    def import_external_agent(self, player_id: int, file_path: str, class_name: str, **kwargs):
        agent = load_external_agent(file_path, class_name, player_id=player_id, **kwargs)
        if player_id == 1:
            self.human_p1 = False
            self.agent1 = agent
            self.p1_mode_idx = -1
        else:
            self.agent2 = agent
            self.p2_mode_idx = -1

    def reset_game(self):
        self.state = GameState.create_default_map(self.state.width, self.state.height)
        if hasattr(self.agent1, "reset_metrics"):
            self.agent1.reset_metrics()
        if hasattr(self.agent2, "reset_metrics"):
            self.agent2.reset_metrics()
        self.tank_anims.clear()
        self.tread_phases = {1: 0, 2: 0}
        self.recoil_timers = {1: 0, 2: 0}
        self.bullet_tracers.clear()
        self.explosions.clear()
        self.particles.clear()
        self.popups.clear()
        self.pending_human_action = None
        self.last_action_text = "Game Reset"

    def step_turn(self):
        if self.state.is_terminal():
            return

        current_pid = self.state.current_player
        if current_pid == 1:
            if self.human_p1:
                if self.pending_human_action is None:
                    return
                action = self.pending_human_action
                self.pending_human_action = None
            else:
                action = self.agent1.get_action(self.state)
        else:
            action = self.agent2.get_action(self.state)

        legal = self.state.get_legal_actions(current_pid)
        if action not in legal:
            action = "STAY"

        # Snapshot before applying action so we can spawn crisp visual effects
        prev_tanks = {
            pid: (t.x, t.y, t.hp, t.direction) for pid, t in self.state.tanks.items()
        }
        prev_bases = {pid: (b.x, b.y, b.hp) for pid, b in self.state.bases.items()}
        prev_walls = {pos: w.hp for pos, w in self.state.walls.items()}

        self.state.apply_action(action)
        self.last_action_text = f"P{current_pid}: {action}"
        self._trigger_turn_effects(current_pid, action, prev_tanks, prev_bases, prev_walls)

    def _trigger_turn_effects(self, acting_pid: int, action: str, prev_tanks: dict, prev_bases: dict, prev_walls: dict):
        now = pygame.time.get_ticks() if pygame.get_init() else 0

        # 1. Tank slide & tread animation
        for pid, tank in self.state.tanks.items():
            px, py, php, _ = prev_tanks[pid]
            if (tank.x, tank.y) != (px, py):
                self.tank_anims[pid] = {
                    "from": (px, py),
                    "to": (tank.x, tank.y),
                    "start": now,
                    "duration": min(140, max(40, self.step_delay_ms // 2)),
                }
                self.tread_phases[pid] = (self.tread_phases[pid] + 1) % 2
            if tank.hp < php:
                self._spawn_hit_fx(tank.x, tank.y, is_big=(tank.hp == 0), color=(255, 160, 60))

        # 2. Firing tracer & barrel recoil
        if action == "FIRE":
            tank = self.state.tanks[acting_pid]
            self.recoil_timers[acting_pid] = now
            dx, dy = DIRECTION_DELTAS[tank.direction]
            # Trace up to 3 cells to visualize bullet path even on immediate impact
            end_x, end_y = tank.x, tank.y
            for step in range(1, 4):
                tx = tank.x + dx * step
                ty = tank.y + dy * step
                if not self.state.is_inside(tx, ty):
                    break
                end_x, end_y = tx, ty
                hit_wall = (tx, ty) in prev_walls
                hit_tank = any(
                    t.x == tx and t.y == ty and prev_tanks[pid][2] > 0
                    for pid, t in self.state.tanks.items()
                )
                hit_base = any(
                    b.x == tx and b.y == ty and prev_bases[pid][2] > 0
                    for pid, b in self.state.bases.items()
                )
                if hit_wall or hit_tank or hit_base:
                    break
            self.bullet_tracers.append({
                "start": (tank.x, tank.y),
                "end": (end_x, end_y),
                "dir": tank.direction,
                "owner": acting_pid,
                "start_ms": now,
                "duration": 140,
            })

        # 3. Wall damage / destruction FX
        for pos, old_hp in prev_walls.items():
            cur_wall = self.state.walls.get(pos)
            new_hp = cur_wall.hp if cur_wall is not None else 0
            if new_hp < old_hp:
                self._spawn_hit_fx(pos[0], pos[1], is_big=(new_hp == 0), color=self.COLOR_BRICK_HI)

        # 4. Base damage / destruction FX
        for pid, (bx, by, old_hp) in prev_bases.items():
            new_hp = self.state.bases[pid].hp
            if new_hp < old_hp:
                self._spawn_hit_fx(bx, by, is_big=(new_hp == 0), color=(255, 220, 90))

    def _spawn_hit_fx(self, gx: int, gy: int, is_big: bool = False, color=(255, 175, 60)):
        now = pygame.time.get_ticks() if pygame.get_init() else 0
        cx, cy = self._cell_center_px(gx, gy)
        self.explosions.append({
            "x": cx,
            "y": cy,
            "start": now,
            "duration": 380 if is_big else 240,
            "max_r": 40 if is_big else 24,
        })
        # Replace any recent popup at the same cell so text never overlaps
        self.popups = [p for p in self.popups if abs(p["x"] - cx) > 8 or abs(p["y"] - (cy - 10)) > 8]
        self.popups.append({
            "x": cx,
            "y": cy - 10,
            "text": "DESTROYED!" if is_big else "-1 HP",
            "color": (255, 95, 85) if is_big else (255, 225, 110),
            "start": now,
            "duration": 650,
        })
        count = 14 if is_big else 7
        for i in range(count):
            angle = (2 * math.pi * i) / count + (i % 3) * 0.2
            speed = 1.6 + (i % 4) * 0.7
            self.particles.append({
                "x": float(cx),
                "y": float(cy),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 1.0,
                "color": color if i % 2 == 0 else (255, 230, 120),
                "size": 4 if is_big else 3,
            })

    def _cell_origin_px(self, gx: int, gy: int) -> tuple:
        return (
            self.BOARD_PADDING + gx * self.CELL_SIZE,
            self.BOARD_PADDING + gy * self.CELL_SIZE,
        )

    def _cell_center_px(self, gx: int, gy: int) -> tuple:
        ox, oy = self._cell_origin_px(gx, gy)
        return ox + self.CELL_SIZE // 2, oy + self.CELL_SIZE // 2

    def _load_font(self, size: int, bold: bool = False):
        return pygame.font.SysFont("arial,helvetica,dejavusans", size, bold=bold)

    def _build_panel_buttons(self, x_offset: int):
        self.buttons = []
        pad_x = x_offset + 16
        card_w = self.PANEL_WIDTH - 32
        inner_x = pad_x + 12
        inner_w = card_w - 24

        # Player 1 mode pills (inside P1 card: y=96..258)
        p1_modes = [
            ("Minimax", "p1_mode_1"),
            ("AlphaBeta", "p1_mode_2"),
            ("H-Minimax", "p1_mode_3"),
            ("H-AlphaBeta", "p1_mode_4"),
            ("Human", "p1_mode_5"),
        ]
        self._add_pill_grid(inner_x, 184, inner_w, p1_modes, "p1_mode")

        # Player 2 mode pills (inside P2 card: y=268..430)
        p2_modes = [
            ("Minimax", "p2_mode_1"),
            ("AlphaBeta", "p2_mode_2"),
            ("H-Minimax", "p2_mode_3"),
            ("H-AlphaBeta", "p2_mode_4"),
            ("Random", "p2_mode_0"),
        ]
        self._add_pill_grid(inner_x, 356, inner_w, p2_modes, "p2_mode")

        # Control action buttons (inside Controls card: y=440..552)
        btn_gap = 8
        ctrl_w = (inner_w - 2 * btn_gap) // 3
        ctrl_y = 454
        self.buttons.append(Button(pygame.Rect(inner_x, ctrl_y, ctrl_w, 30), "Pause/Play", "toggle_pause", "ctrl"))
        self.buttons.append(Button(pygame.Rect(inner_x + ctrl_w + btn_gap, ctrl_y, ctrl_w, 30), "Step +1", "step_once", "ctrl"))
        self.buttons.append(Button(pygame.Rect(inner_x + 2 * (ctrl_w + btn_gap), ctrl_y, ctrl_w, 30), "Reset", "reset_game", "ctrl"))

        # Speed buttons
        spd_gap = 6
        spd_w = (inner_w - 3 * spd_gap) // 4
        spd_y = 494
        for idx, (label, delay_ms) in enumerate(self.SPEED_PRESETS):
            bx = inner_x + idx * (spd_w + spd_gap)
            self.buttons.append(Button(pygame.Rect(bx, spd_y, spd_w, 26), label, f"speed_{delay_ms}", "speed"))

    def _add_pill_grid(self, x: int, y: int, total_w: int, items: list, group: str):
        gap = 6
        row1_w = (total_w - 2 * gap) // 3
        for idx in range(3):
            label, act = items[idx]
            rect = pygame.Rect(x + idx * (row1_w + gap), y, row1_w, 26)
            self.buttons.append(Button(rect, label, act, group))

        row2_w = (total_w - gap) // 2
        for idx in range(2):
            label, act = items[3 + idx]
            rect = pygame.Rect(x + idx * (row2_w + gap), y + 32, row2_w, 26)
            self.buttons.append(Button(rect, label, act, group))

    def _handle_button_click(self, action_id: str):
        if action_id == "toggle_pause":
            self.paused = not self.paused
        elif action_id == "step_once":
            self.paused = True
            self.step_turn()
        elif action_id == "reset_game":
            self.reset_game()
        elif action_id.startswith("speed_"):
            self.step_delay_ms = int(action_id.split("_")[1])
        elif action_id == "p1_mode_5":
            self.human_p1 = True
            self.p1_mode_idx = 5
        elif action_id.startswith("p1_mode_"):
            self.set_agent_mode(1, int(action_id.split("_")[2]))
        elif action_id.startswith("p2_mode_"):
            self.set_agent_mode(2, int(action_id.split("_")[2]))

    def run(self):
        pygame.init()
        board_area_w = self.state.width * self.CELL_SIZE + 2 * self.BOARD_PADDING
        board_area_h = self.state.height * self.CELL_SIZE + 2 * self.BOARD_PADDING
        screen_w = board_area_w + self.PANEL_WIDTH
        screen_h = max(board_area_h, 668)

        screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption("Task 2: Tank Battle Arena - Adversarial Search")
        clock = pygame.time.Clock()

        fonts = {
            "title": self._load_font(20, bold=True),
            "header": self._load_font(15, bold=True),
            "body": self._load_font(14, bold=False),
            "small": self._load_font(12, bold=False),
            "small_bold": self._load_font(12, bold=True),
            "banner": self._load_font(28, bold=True),
        }

        self._build_panel_buttons(board_area_w)
        last_step_time = pygame.time.get_ticks()
        running = True

        while running:
            now = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.buttons:
                        if btn.rect.collidepoint(event.pos):
                            self._handle_button_click(btn.action_id)
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_s:
                        self.paused = True
                        self.step_turn()
                    elif event.key == pygame.K_1:
                        self.set_agent_mode(1, 1)
                    elif event.key == pygame.K_2:
                        self.set_agent_mode(1, 2)
                    elif event.key == pygame.K_3:
                        self.set_agent_mode(1, 3)
                    elif event.key == pygame.K_4:
                        self.set_agent_mode(1, 4)
                    elif event.key == pygame.K_5:
                        self.human_p1 = True
                        self.p1_mode_idx = 5
                    elif event.key == pygame.K_6:
                        self.set_agent_mode(2, 1)
                    elif event.key == pygame.K_7:
                        self.set_agent_mode(2, 2)
                    elif event.key == pygame.K_8:
                        self.set_agent_mode(2, 3)
                    elif event.key == pygame.K_9:
                        self.set_agent_mode(2, 4)
                    elif event.key == pygame.K_0:
                        self.set_agent_mode(2, 0)
                    elif self.human_p1 and self.state.current_player == 1:
                        if event.key == pygame.K_UP:
                            self.pending_human_action = "MOVE_UP"
                        elif event.key == pygame.K_DOWN:
                            self.pending_human_action = "MOVE_DOWN"
                        elif event.key == pygame.K_LEFT:
                            self.pending_human_action = "MOVE_LEFT"
                        elif event.key == pygame.K_RIGHT:
                            self.pending_human_action = "MOVE_RIGHT"
                        elif event.key == pygame.K_f:
                            self.pending_human_action = "FIRE"
                        elif event.key == pygame.K_w:
                            self.pending_human_action = "STAY"

            if not self.paused and not self.state.is_terminal():
                if self.human_p1 and self.state.current_player == 1:
                    if self.pending_human_action is not None:
                        self.step_turn()
                        last_step_time = now
                elif now - last_step_time >= self.step_delay_ms:
                    self.step_turn()
                    last_step_time = now

            self._update_particles()

            screen.fill(self.COLOR_BG)
            self._draw_board(screen, fonts, now, board_area_w, board_area_h)
            self._draw_panel(screen, board_area_w, screen_h, fonts, mouse_pos)
            pygame.display.flip()
            clock.tick(self.FPS)

        pygame.quit()

    def _update_particles(self):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vx"] *= 0.92
            p["vy"] *= 0.92
            p["life"] -= 0.045
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

    def _draw_board(self, screen, fonts: dict, now: int, area_w: int, area_h: int):
        cs = self.CELL_SIZE
        pad = self.BOARD_PADDING
        board_w = self.state.width * cs
        board_h = self.state.height * cs

        # Steel perimeter frame (Battle City style border)
        outer_rect = pygame.Rect(6, 6, area_w - 12, area_h - 12)
        pygame.draw.rect(screen, self.COLOR_FRAME_OUTER, outer_rect, border_radius=8)
        inner_frame = pygame.Rect(10, 10, area_w - 20, area_h - 20)
        pygame.draw.rect(screen, self.COLOR_FRAME_INNER, inner_frame, border_radius=6)

        # Corner rivets on frame
        for rx, ry in [(14, 14), (area_w - 14, 14), (14, area_h - 14), (area_w - 14, area_h - 14)]:
            pygame.draw.circle(screen, (95, 108, 128), (rx, ry), 3)

        # Checkerboard dark battlefield tiles
        board_rect = pygame.Rect(pad, pad, board_w, board_h)
        pygame.draw.rect(screen, self.COLOR_BOARD_BG, board_rect)
        for y in range(self.state.height):
            for x in range(self.state.width):
                ox, oy = self._cell_origin_px(x, y)
                tile_rect = pygame.Rect(ox, oy, cs, cs)
                if (x + y) % 2 == 1:
                    pygame.draw.rect(screen, self.COLOR_TILE_ALT, tile_rect)
                pygame.draw.rect(screen, self.COLOR_GRID, tile_rect, 1)

        # Draw brick walls
        for (wx, wy), wall in self.state.walls.items():
            if wall.is_alive():
                ox, oy = self._cell_origin_px(wx, wy)
                self._draw_brick_wall(screen, pygame.Rect(ox + 3, oy + 3, cs - 6, cs - 6), wall)

        # Draw command bases
        for pid, base in self.state.bases.items():
            ox, oy = self._cell_origin_px(base.x, base.y)
            self._draw_base(screen, pygame.Rect(ox + 3, oy + 3, cs - 6, cs - 6), base, pid, fonts, now)

        # Draw tanks with smooth movement interpolation & recoil
        for pid, tank in self.state.tanks.items():
            if not tank.is_alive():
                continue
            gx, gy = float(tank.x), float(tank.y)
            anim = self.tank_anims.get(pid)
            if anim is not None:
                t = (now - anim["start"]) / max(1, anim["duration"])
                if t >= 1.0:
                    del self.tank_anims[pid]
                else:
                    fx, fy = anim["from"]
                    tx, ty = anim["to"]
                    gx = fx + (tx - fx) * t
                    gy = fy + (ty - fy) * t

            cx = int(pad + gx * cs + cs // 2)
            cy = int(pad + gy * cs + cs // 2)
            recoil_dt = now - self.recoil_timers.get(pid, 0)
            recoil_px = 4 if 0 <= recoil_dt < 90 else 0
            is_turn = (not self.state.is_terminal()) and (self.state.current_player == pid)
            self._draw_tank(screen, cx, cy, tank, pid, recoil_px, self.tread_phases[pid], is_turn, fonts)

        # Draw tracer bullet animations (visualizes rapid 3-cell flight)
        active_tracers = []
        for tr in self.bullet_tracers:
            progress = (now - tr["start_ms"]) / max(1, tr["duration"])
            if progress < 1.0:
                sx, sy = self._cell_center_px(*tr["start"])
                ex, ey = self._cell_center_px(*tr["end"])
                bx = int(sx + (ex - sx) * progress)
                by = int(sy + (ey - sy) * progress)
                # Muzzle flash near barrel when just fired
                if progress < 0.35:
                    dx, dy = DIRECTION_DELTAS[tr["dir"]]
                    fx, fy = sx + dx * 22, sy + dy * 22
                    pygame.draw.circle(screen, (255, 240, 160), (fx, fy), 9)
                self._draw_bullet(screen, bx, by, tr["dir"], tr["owner"])
                active_tracers.append(tr)
        self.bullet_tracers = active_tracers

        # Draw persistent active bullets from GameState
        for bullet in self.state.bullets:
            if bullet.active:
                bx, by = self._cell_center_px(bullet.x, bullet.y)
                self._draw_bullet(screen, bx, by, bullet.direction, bullet.owner_id)

        # Draw explosions & particles & damage popups
        self._draw_fx_layers(screen, fonts, now)

        # Victory overlay banner on board
        if self.state.is_terminal():
            self._draw_victory_overlay(screen, board_rect, fonts)

    def _draw_brick_wall(self, screen, rect: pygame.Rect, wall):
        # Mortar background
        pygame.draw.rect(screen, self.COLOR_MORTAR, rect, border_radius=3)

        rows = 4
        cols = 2
        row_h = (rect.h - (rows + 1) * 2) // rows
        col_w = (rect.w - (cols + 1) * 2) // cols

        # Determine which brick cells remain based on HP (3=full, 2=chipped, 1=heavy damage)
        missing_bricks = set()
        if wall.hp == 2:
            missing_bricks = {(0, 1), (3, 0)}
        elif wall.hp == 1:
            missing_bricks = {(0, 0), (0, 1), (2, 1), (3, 0)}

        for r in range(rows):
            offset = (col_w // 3) if r % 2 == 1 else 0
            for c in range(cols + 1):
                if (r, c % cols) in missing_bricks:
                    continue
                bx = rect.x + 2 + c * (col_w + 2) - offset
                by = rect.y + 2 + r * (row_h + 2)
                bw = col_w
                # Clip brick inside wall bounds
                brick_rect = pygame.Rect(bx, by, bw, row_h).clip(rect.inflate(-2, -2))
                if brick_rect.w > 3 and brick_rect.h > 2:
                    pygame.draw.rect(screen, self.COLOR_BRICK, brick_rect, border_radius=1)
                    pygame.draw.line(screen, self.COLOR_BRICK_HI, (brick_rect.x, brick_rect.y), (brick_rect.right - 1, brick_rect.y), 2)
                    pygame.draw.line(screen, self.COLOR_BRICK_SH, (brick_rect.x, brick_rect.bottom - 1), (brick_rect.right - 1, brick_rect.bottom - 1), 2)

        # Crack lines if damaged
        if wall.hp < wall.INITIAL_HP:
            pygame.draw.line(screen, (30, 16, 12), (rect.x + 8, rect.y + 8), (rect.centerx, rect.centery + 4), 2)
            pygame.draw.line(screen, (30, 16, 12), (rect.centerx, rect.centery + 4), (rect.right - 10, rect.bottom - 10), 2)

        # Clean 3-segment HP indicator at bottom
        self._draw_segmented_bar(screen, rect.x + 4, rect.bottom - 7, rect.w - 8, 4, wall.hp, wall.INITIAL_HP)

    def _draw_base(self, screen, rect: pygame.Rect, base, pid: int, fonts: dict, now: int):
        main_c = self.COLOR_P1_MAIN if pid == 1 else self.COLOR_P2_MAIN
        dark_c = self.COLOR_P1_DARK if pid == 1 else self.COLOR_P2_DARK
        light_c = self.COLOR_P1_LIGHT if pid == 1 else self.COLOR_P2_LIGHT

        # Armored base foundation
        pygame.draw.rect(screen, (38, 44, 54), rect, border_radius=6)
        pygame.draw.rect(screen, dark_c, rect.inflate(-4, -4), border_radius=5)

        if not base.is_alive():
            # Ruined base crater
            pygame.draw.circle(screen, (28, 28, 32), rect.center, rect.w // 3)
            pygame.draw.line(screen, (95, 45, 45), (rect.x + 12, rect.y + 12), (rect.right - 12, rect.bottom - 12), 4)
            pygame.draw.line(screen, (95, 45, 45), (rect.right - 12, rect.y + 12), (rect.x + 12, rect.bottom - 12), 4)
            return

        # Warning pulse if low HP
        border_col = light_c
        if base.hp <= 3 and (now // 220) % 2 == 0:
            border_col = (255, 220, 90)
        pygame.draw.rect(screen, border_col, rect, 2, border_radius=6)

        # Classic Battle City Eagle / Phoenix Emblem (scaled neatly below top label)
        cx, cy = rect.centerx, rect.centery + 3
        wing_pts = [
            (cx, cy - 10),
            (cx + 5, cy - 13),
            (cx + 17, cy - 8),
            (cx + 14, cy + 4),
            (cx + 7, cy + 2),
            (cx + 9, cy + 12),
            (cx, cy + 8),
            (cx - 9, cy + 12),
            (cx - 7, cy + 2),
            (cx - 14, cy + 4),
            (cx - 17, cy - 8),
            (cx - 5, cy - 13),
        ]
        pygame.draw.polygon(screen, light_c, wing_pts)
        pygame.draw.polygon(screen, (255, 255, 255), wing_pts, 1)
        # Central shield star
        pygame.draw.circle(screen, main_c, (cx, cy - 1), 5)
        pygame.draw.circle(screen, (255, 245, 190), (cx, cy - 1), 2)

        # Base HP bar & top-left tag
        self._draw_hp_bar(screen, rect.x + 5, rect.bottom - 8, rect.w - 10, 5, base.hp, base.INITIAL_HP)
        tag = fonts["small_bold"].render(f"B{pid}:{base.hp}", True, self.COLOR_TEXT)
        screen.blit(tag, (rect.x + 5, rect.y + 2))

    def _draw_tank(
        self,
        screen,
        cx: int,
        cy: int,
        tank,
        pid: int,
        recoil_px: int,
        tread_phase: int,
        is_turn: bool,
        fonts: dict,
    ):
        main_c = self.COLOR_P1_MAIN if pid == 1 else self.COLOR_P2_MAIN
        light_c = self.COLOR_P1_LIGHT if pid == 1 else self.COLOR_P2_LIGHT
        dark_c = self.COLOR_P1_DARK if pid == 1 else self.COLOR_P2_DARK
        tread_c = self.COLOR_P1_TREAD if pid == 1 else self.COLOR_P2_TREAD

        # Tactical corner brackets around the active turn cell
        if is_turn:
            cs = self.CELL_SIZE
            cell_x = cx - cs // 2 + 4
            cell_y = cy - cs // 2 + 4
            cell_r = cell_x + cs - 8
            cell_b = cell_y + cs - 8
            bl = 10
            for (px, py, sx, sy) in [
                (cell_x, cell_y, 1, 1),
                (cell_r, cell_y, -1, 1),
                (cell_x, cell_b, 1, -1),
                (cell_r, cell_b, -1, -1),
            ]:
                pygame.draw.line(screen, light_c, (px, py), (px + sx * bl, py), 2)
                pygame.draw.line(screen, light_c, (px, py), (px, py + sy * bl), 2)

        is_vertical = tank.direction in ("UP", "DOWN")
        hull_w, hull_h = (32, 40) if is_vertical else (40, 32)
        hull_rect = pygame.Rect(cx - hull_w // 2, cy - hull_h // 2 + 3, hull_w, hull_h)
        turret_cy = hull_rect.centery

        # 1. Left & Right Caterpillar Tracks with tread cleats
        if is_vertical:
            tread_l = pygame.Rect(hull_rect.x - 4, hull_rect.y + 1, 9, hull_h - 2)
            tread_r = pygame.Rect(hull_rect.right - 5, hull_rect.y + 1, 9, hull_h - 2)
            for tr in (tread_l, tread_r):
                pygame.draw.rect(screen, tread_c, tr, border_radius=3)
                for off in range(4 + tread_phase * 3, tr.h - 3, 7):
                    pygame.draw.line(screen, (95, 106, 124), (tr.x + 1, tr.y + off), (tr.right - 2, tr.y + off), 2)
        else:
            tread_t = pygame.Rect(hull_rect.x + 1, hull_rect.y - 4, hull_w - 2, 9)
            tread_b = pygame.Rect(hull_rect.x + 1, hull_rect.bottom - 5, hull_w - 2, 9)
            for tr in (tread_t, tread_b):
                pygame.draw.rect(screen, tread_c, tr, border_radius=3)
                for off in range(4 + tread_phase * 3, tr.w - 3, 7):
                    pygame.draw.line(screen, (95, 106, 124), (tr.x + off, tr.y + 1), (tr.x + off, tr.bottom - 2), 2)

        # 2. Main Armored Hull with 3D bevel
        inner_hull = hull_rect.inflate(-6, -6)
        pygame.draw.rect(screen, dark_c, inner_hull, border_radius=5)
        pygame.draw.rect(screen, main_c, inner_hull.inflate(-4, -4), border_radius=4)

        # 3. Cannon Barrel + Muzzle Brake
        dx, dy = DIRECTION_DELTAS[tank.direction]
        barrel_len = 24 - recoil_px
        bx_end = cx + dx * barrel_len
        by_end = turret_cy + dy * barrel_len
        pygame.draw.line(screen, (36, 42, 52), (cx, turret_cy), (bx_end, by_end), 7)
        pygame.draw.line(screen, (218, 226, 238), (cx, turret_cy), (bx_end, by_end), 3)
        pygame.draw.circle(screen, (242, 246, 252), (bx_end, by_end), 3)

        # 4. Turret Dome & Hatch
        pygame.draw.circle(screen, dark_c, (cx, turret_cy), 11)
        pygame.draw.circle(screen, light_c, (cx, turret_cy), 8)
        pygame.draw.circle(screen, main_c, (cx, turret_cy), 4)

        # 5. Tank HP bar & compact team badge neatly aligned at top of cell
        bar_w = self.CELL_SIZE - 26
        bar_x = cx - self.CELL_SIZE // 2 + 20
        bar_y = cy - self.CELL_SIZE // 2 + 6
        p_lbl = fonts["small_bold"].render(f"P{pid}", True, light_c)
        screen.blit(p_lbl, (cx - self.CELL_SIZE // 2 + 4, bar_y - 4))
        self._draw_hp_bar(screen, bar_x, bar_y, bar_w, 5, tank.hp, tank.INITIAL_HP)

    def _draw_bullet(self, screen, px: int, py: int, direction: str, owner_id: int):
        dx, dy = DIRECTION_DELTAS[direction]
        aura_col = (120, 210, 255) if owner_id == 1 else (255, 130, 100)

        # Trailing flame behind bullet
        tx, ty = px - dx * 12, py - dy * 12
        pygame.draw.line(screen, aura_col, (tx, ty), (px, py), 5)
        pygame.draw.circle(screen, self.COLOR_BULLET_GLOW, (px, py), 7)

        # Pointed warhead tip
        perp_x, perp_y = -dy, dx
        tip = (px + dx * 9, py + dy * 9)
        left = (px - dx * 4 + perp_x * 4, py - dy * 4 + perp_y * 4)
        right = (px - dx * 4 - perp_x * 4, py - dy * 4 - perp_y * 4)
        pygame.draw.polygon(screen, self.COLOR_BULLET_CORE, [tip, left, right])

    def _draw_fx_layers(self, screen, fonts: dict, now: int):
        # Explosions (Battle City starburst blast + expanding shockwave ring)
        alive_exp = []
        for exp in self.explosions:
            prog = (now - exp["start"]) / max(1, exp["duration"])
            if prog < 1.0:
                outer_r = max(4, int(exp["max_r"] * (0.35 + 0.65 * prog)))
                inner_r = max(2, int(outer_r * 0.45))
                star_pts = []
                for k in range(16):
                    ang = k * (math.pi / 8.0)
                    rad = outer_r if k % 2 == 0 else inner_r
                    star_pts.append((exp["x"] + int(math.cos(ang) * rad), exp["y"] + int(math.sin(ang) * rad)))
                pygame.draw.polygon(screen, (255, 115, 35), star_pts)
                if prog < 0.7:
                    pygame.draw.circle(screen, (255, 238, 145), (exp["x"], exp["y"]), max(2, inner_r))
                pygame.draw.circle(screen, (255, 190, 90), (exp["x"], exp["y"]), max(3, int(exp["max_r"] * prog)), 2)
                alive_exp.append(exp)
        self.explosions = alive_exp

        # Spark / brick debris particles
        for p in self.particles:
            r = max(1, int(p["size"] * p["life"]))
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), r)

        # Floating damage popups with dark drop shadow for readability
        alive_pop = []
        for pop in self.popups:
            prog = (now - pop["start"]) / max(1, pop["duration"])
            if prog < 1.0:
                dy_off = int(20 * prog)
                tx = pop["x"]
                ty = pop["y"] - dy_off
                shadow_surf = fonts["small_bold"].render(pop["text"], True, (12, 14, 18))
                surf = fonts["small_bold"].render(pop["text"], True, pop["color"])
                px = tx - surf.get_width() // 2
                screen.blit(shadow_surf, (px + 1, ty + 1))
                screen.blit(surf, (px, ty))
                alive_pop.append(pop)
        self.popups = alive_pop

    def _draw_victory_overlay(self, screen, board_rect: pygame.Rect, fonts: dict):
        overlay = pygame.Surface((board_rect.w, 120), pygame.SRCALPHA)
        overlay.fill((12, 16, 22, 215))
        oy = board_rect.centery - 60
        screen.blit(overlay, (board_rect.x, oy))
        pygame.draw.rect(screen, self.COLOR_CARD_BORDER, (board_rect.x, oy, board_rect.w, 120), 2)

        winner = self.state.get_winner()
        if winner == 1:
            msg = "PLAYER 1 (BLUE) VICTORY!"
            col = self.COLOR_P1_LIGHT
        elif winner == 2:
            msg = "PLAYER 2 (RED) VICTORY!"
            col = self.COLOR_P2_LIGHT
        else:
            msg = "MATCH DRAW!"
            col = (241, 196, 15)

        title_surf = fonts["banner"].render(msg, True, col)
        sub_surf = fonts["body"].render("Press [R] or click Reset to start a new match", True, self.COLOR_TEXT)
        screen.blit(title_surf, (board_rect.centerx - title_surf.get_width() // 2, oy + 26))
        screen.blit(sub_surf, (board_rect.centerx - sub_surf.get_width() // 2, oy + 72))

    def _hp_color(self, hp: int, max_hp: int) -> tuple:
        ratio = hp / max(1, max_hp)
        if ratio > 0.5:
            return self.COLOR_HP_GREEN
        if ratio > 0.25:
            return self.COLOR_HP_YELLOW
        return self.COLOR_HP_RED

    def _draw_hp_bar(self, screen, x: int, y: int, width: int, height: int, hp: int, max_hp: int):
        pygame.draw.rect(screen, self.COLOR_HP_BG, (x, y, width, height), border_radius=2)
        fill_w = int(width * max(0, hp) / max(1, max_hp))
        if fill_w > 0:
            pygame.draw.rect(screen, self._hp_color(hp, max_hp), (x, y, fill_w, height), border_radius=2)

    def _draw_segmented_bar(self, screen, x: int, y: int, width: int, height: int, hp: int, max_hp: int):
        gap = 2
        seg_w = (width - (max_hp - 1) * gap) // max(1, max_hp)
        col = self._hp_color(hp, max_hp)
        for i in range(max_hp):
            sx = x + i * (seg_w + gap)
            c = col if i < hp else self.COLOR_HP_BG
            pygame.draw.rect(screen, c, (sx, y, seg_w, height), border_radius=1)

    def _draw_panel(self, screen, x_offset: int, height: int, fonts: dict, mouse_pos: tuple):
        panel_rect = pygame.Rect(x_offset, 0, self.PANEL_WIDTH, height)
        pygame.draw.rect(screen, self.COLOR_PANEL, panel_rect)
        pygame.draw.line(screen, self.COLOR_CARD_BORDER, (x_offset, 0), (x_offset, height), 2)

        pad_x = x_offset + 16
        card_w = self.PANEL_WIDTH - 32

        # 1. Header Card (y=12..84)
        self._draw_card(screen, pygame.Rect(pad_x, 12, card_w, 72))
        title = fonts["title"].render("TANK BATTLE - AI ARENA", True, self.COLOR_TEXT)
        screen.blit(title, (pad_x + 12, 20))

        if self.state.is_terminal():
            w = self.state.get_winner()
            badge_txt = f"WINNER: P{w}" if w else "DRAW"
            badge_col = self.COLOR_P1_MAIN if w == 1 else (self.COLOR_P2_MAIN if w == 2 else (241, 196, 15))
        elif self.paused:
            badge_txt = "PAUSED"
            badge_col = (241, 196, 15)
        else:
            badge_txt = "RUNNING"
            badge_col = self.COLOR_HP_GREEN

        badge_rect = pygame.Rect(pad_x + card_w - 102, 18, 90, 24)
        pygame.draw.rect(screen, badge_col, badge_rect, border_radius=4)
        b_surf = fonts["small_bold"].render(badge_txt, True, (15, 18, 24))
        screen.blit(b_surf, (badge_rect.centerx - b_surf.get_width() // 2, badge_rect.centery - b_surf.get_height() // 2))

        turn_str = f"Turn: {self.state.turn_count}/{self.state.max_turns}  |  Active: P{self.state.current_player}  |  Last: {self.last_action_text}"
        screen.blit(fonts["small"].render(turn_str, True, self.COLOR_SUBTEXT), (pad_x + 12, 54))

        # 2. Player 1 Card (y=94..256)
        self._draw_player_card(screen, pad_x, 94, card_w, 162, 1, fonts)

        # 3. Player 2 Card (y=266..428)
        self._draw_player_card(screen, pad_x, 266, card_w, 162, 2, fonts)

        # 4. Controls & Speed Card (y=438..534)
        self._draw_card(screen, pygame.Rect(pad_x, 438, card_w, 94))

        # 5. Draw all interactive buttons
        for btn in self.buttons:
            self._draw_button(screen, btn, mouse_pos, fonts)

        # 6. Keyboard Legend Card (y=542..652)
        self._draw_card(screen, pygame.Rect(pad_x, 542, card_w, 110))
        lx = pad_x + 12
        ly = 550
        screen.blit(fonts["small_bold"].render("KEYBOARD SHORTCUTS", True, self.COLOR_TEXT), (lx, ly))
        legend_rows = [
            "SPACE: Play / Pause    S: Step 1 Turn    R: Reset",
            "P1 Mode: [1] Minimax [2] AB [3] H-MM [4] H-AB [5] Human",
            "P2 Mode: [6] Minimax [7] AB [8] H-MM [9] H-AB [0] Random",
            "Human P1: Arrows = Move  |  F = Fire  |  W = Stay",
        ]
        for idx, line in enumerate(legend_rows):
            screen.blit(fonts["small"].render(line, True, self.COLOR_SUBTEXT), (lx, ly + 20 + idx * 20))

    def _draw_card(self, screen, rect: pygame.Rect, accent_color=None):
        pygame.draw.rect(screen, self.COLOR_CARD, rect, border_radius=8)
        border = accent_color if accent_color else self.COLOR_CARD_BORDER
        pygame.draw.rect(screen, border, rect, 1, border_radius=8)

    def _draw_player_card(self, screen, x: int, y: int, w: int, h: int, pid: int, fonts: dict):
        is_turn = (not self.state.is_terminal()) and (self.state.current_player == pid)
        main_col = self.COLOR_P1_MAIN if pid == 1 else self.COLOR_P2_MAIN
        light_col = self.COLOR_P1_LIGHT if pid == 1 else self.COLOR_P2_LIGHT

        self._draw_card(screen, pygame.Rect(x, y, w, h), accent_color=main_col if is_turn else None)

        ix = x + 12
        role = "MAX - BLUE" if pid == 1 else "MIN - RED"
        agent = self.agent1 if pid == 1 else self.agent2
        mode_name = "Human (Keyboard)" if (pid == 1 and self.human_p1) else agent.name

        header = fonts["header"].render(f"PLAYER {pid} ({role})", True, light_col)
        screen.blit(header, (ix, y + 10))
        if is_turn:
            turn_tag = fonts["small_bold"].render("ACTIVE", True, (15, 18, 24))
            t_rect = pygame.Rect(x + w - 68, y + 10, 56, 18)
            pygame.draw.rect(screen, light_col, t_rect, border_radius=3)
            screen.blit(turn_tag, (t_rect.centerx - turn_tag.get_width() // 2, t_rect.centery - turn_tag.get_height() // 2))

        # Tank HP & Base HP bars
        tank = self.state.tanks[pid]
        base = self.state.bases[pid]
        half_w = (w - 36) // 2

        screen.blit(fonts["small"].render(f"Tank HP: {tank.hp}/{tank.INITIAL_HP}", True, self.COLOR_TEXT), (ix, y + 34))
        self._draw_hp_bar(screen, ix, y + 51, half_w, 7, tank.hp, tank.INITIAL_HP)

        bx = ix + half_w + 12
        screen.blit(fonts["small"].render(f"Base HP: {base.hp}/{base.INITIAL_HP}", True, self.COLOR_TEXT), (bx, y + 34))
        self._draw_hp_bar(screen, bx, y + 51, half_w, 7, base.hp, base.INITIAL_HP)

        # Telemetry
        states_val = getattr(agent, "explored_states", 0)
        time_ms = getattr(agent, "last_decision_time", 0.0) * 1000.0
        tele_str = f"AI: {mode_name}  |  States: {states_val}  |  {time_ms:.2f} ms"
        screen.blit(fonts["small"].render(tele_str, True, self.COLOR_SUBTEXT), (ix, y + 66))

    def _is_button_active(self, btn: Button) -> bool:
        if btn.group == "p1_mode":
            return int(btn.action_id.split("_")[2]) == self.p1_mode_idx
        if btn.group == "p2_mode":
            return int(btn.action_id.split("_")[2]) == self.p2_mode_idx
        if btn.group == "speed":
            return int(btn.action_id.split("_")[1]) == self.step_delay_ms
        if btn.action_id == "toggle_pause":
            return self.paused
        return False

    def _draw_button(self, screen, btn: Button, mouse_pos: tuple, fonts: dict):
        active = self._is_button_active(btn)
        hovered = btn.rect.collidepoint(mouse_pos)

        if active:
            if btn.group == "p1_mode":
                bg = self.COLOR_P1_MAIN
            elif btn.group == "p2_mode":
                bg = self.COLOR_P2_MAIN
            elif btn.group == "speed":
                bg = (46, 160, 110)
            else:
                bg = (210, 155, 45)
            txt_col = (15, 18, 24)
        else:
            bg = self.COLOR_BTN_HOVER if hovered else self.COLOR_BTN
            txt_col = self.COLOR_BTN_TEXT

        pygame.draw.rect(screen, bg, btn.rect, border_radius=5)
        if not active:
            pygame.draw.rect(screen, self.COLOR_CARD_BORDER, btn.rect, 1, border_radius=5)

        label = btn.label
        if btn.action_id == "toggle_pause":
            label = "Resume" if self.paused else "Pause"

        surf = fonts["small_bold"].render(label, True, txt_col)
        screen.blit(surf, (btn.rect.centerx - surf.get_width() // 2, btn.rect.centery - surf.get_height() // 2))
