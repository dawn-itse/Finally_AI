import importlib.util
import os
import random


class BaseAgent:
    def __init__(self, player_id: int, name: str = "BaseAgent"):
        self.player_id = player_id
        self.name = name

    def get_action(self, state) -> str:
        raise NotImplementedError("Subclasses must implement get_action(state).")


class RandomAgent(BaseAgent):
    def __init__(self, player_id: int):
        super().__init__(player_id, name="RandomAgent")

    def get_action(self, state) -> str:
        legal_actions = state.get_legal_actions(self.player_id)
        return random.choice(legal_actions)


def load_external_agent(file_path: str, class_name: str, player_id: int, **kwargs) -> BaseAgent:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Agent file not found: {file_path}")

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, class_name):
        raise AttributeError(f"Class '{class_name}' not found in {file_path}")

    agent_cls = getattr(module, class_name)
    return agent_cls(player_id=player_id, **kwargs)
