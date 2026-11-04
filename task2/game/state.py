class GameState:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tanks = {}
        self.bases = {}
        self.walls = {}
        self.bullets = []
        self.current_player = 1

    def is_terminal(self) -> bool:
        pass

    def get_legal_actions(self, player_id: int) -> list:
        pass

    def apply_action(self, player_id: int, action: str):
        pass
