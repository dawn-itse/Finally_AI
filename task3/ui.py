import pygame


class KakuroUI:
    def __init__(self, csp, solver):
        self.csp = csp
        self.solver = solver
        self.cell_size = 58
        self.reset()

    def reset(self):
        self.domains = self.csp.domains.copy()
        self.position = 0
        self.active = None
        self.playing = False
        self.message = "Ready"

    def step(self):
        if self.position < len(self.solver.steps):
            self.active, cell, changes, detail = self.solver.steps[self.position]
            self.domains.update(changes)
            row, col = cell
            self.message = f"{detail}  (row {row + 1}, col {col + 1})"
            self.position += 1
        if self.position == len(self.solver.steps):
            self.playing = False

    def step_back(self):
        self.playing = False
        if self.position == 0:
            return
        target = self.position - 1
        # Phát lại đến bước đích để khôi phục miền và màu từ cùng một nhật ký.
        self.reset()
        for _ in range(target):
            self.step()

    def _label(self, text, position, font, color, centered=False):
        surface = font.render(str(text), True, color)
        rect = surface.get_rect(center=position) if centered else position
        self.screen.blit(surface, rect)

    def draw(self):
        self.screen.fill((231, 237, 242))
        white, ink = (250, 250, 250), (25, 36, 49)
        highlights = {
            "assign": (180, 220, 255),
            "prune": (255, 227, 160),
            "backtrack": (255, 185, 185),
        }
        changes = self.solver.steps[self.position - 1][2] if self.active else {}
        size = self.cell_size
        for row, line in enumerate(self.csp.board_data):
            for col, clue in enumerate(line):
                x, y = 18 + col * size, 18 + row * size
                rect = pygame.Rect(x, y, size, size)
                if clue is None:
                    color = highlights[self.active] if (row, col) in changes else white
                    pygame.draw.rect(self.screen, color, rect)
                    values = self.domains[row, col]
                    if len(values) <= 1:
                        self._label(next(iter(values), "X"), rect.center, self.large, ink, True)
                    else:
                        # Hiện miền theo lưới 3×3 để dễ thấy số nào bị loại.
                        for value in sorted(values):
                            r, c = divmod(value - 1, 3)
                            self._label(value, (x + 11 + 18*c, y + 11 + 18*r),
                                        self.small, ink, True)
                else:
                    pygame.draw.rect(self.screen, ink, rect)
                    if isinstance(clue, tuple):
                        across, down = clue
                        pygame.draw.line(self.screen, white, rect.topleft, rect.bottomright)
                        if across:
                            self._label(across, (x + 43, y + 13), self.small, white, True)
                        if down:
                            self._label(down, (x + 14, y + 44), self.small, white, True)
                pygame.draw.rect(self.screen, (95, 110, 125), rect, 1)

        y = 26 + len(self.csp.board_data) * size
        self._label("Left: back    Right: step    Space: play / pause    R: reset",
                    (18, y), self.small, ink)
        self._label("Blue: assign    Yellow: prune    Red: backtrack", (18, y + 20), self.small, ink)
        status = ""
        if self.position == len(self.solver.steps):
            status = "Solved | " if self.solver.solution is not None else "No solution | "
        self._label(f"{self.position}/{len(self.solver.steps)}  {status}{self.message}",
                    (18, y + 40), self.small, ink)

    def run(self):
        # Giải trước, sau đó phát lại các bước để UI có thể tạm dừng và đặt lại.
        self.solver.solve()
        self.reset()
        pygame.init()
        try:
            width = max(560, len(self.csp.board_data[0]) * self.cell_size + 36)
            height = len(self.csp.board_data) * self.cell_size + 92
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Task 3 - Kakuro CSP")
            self.small = pygame.font.Font(None, 20)
            self.large = pygame.font.Font(None, 38)
            clock = pygame.time.Clock()
            last_step = 0
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RIGHT:
                            self.playing = False
                            self.step()
                        elif event.key == pygame.K_LEFT:
                            self.step_back()
                        elif event.key == pygame.K_SPACE:
                            self.playing = not self.playing
                            last_step = pygame.time.get_ticks()
                        elif event.key == pygame.K_r:
                            self.reset()
                now = pygame.time.get_ticks()
                if self.playing and now - last_step >= 160:
                    self.step()
                    last_step = now
                self.draw()
                pygame.display.flip()
                clock.tick(60)
        finally:
            pygame.quit()
