class BaseAgent:
    def __init__(self, player_id: int):
        self.player_id = player_id

    def get_action(self, state) -> str:
        raise NotImplementedError
