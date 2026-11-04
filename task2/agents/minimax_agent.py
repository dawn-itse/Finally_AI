from agents.base_agent import BaseAgent


class MinimaxAgent(BaseAgent):
    def __init__(self, player_id: int, depth: int = 3, use_alpha_beta: bool = False, use_heuristic: bool = True):
        super().__init__(player_id)
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.use_heuristic = use_heuristic
        self.explored_states = 0

    def get_action(self, state) -> str:
        pass
