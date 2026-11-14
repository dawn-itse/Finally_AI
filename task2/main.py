import argparse
from agents.minimax_agent import MinimaxAgent
from game.state import GameState


def create_midgame_scenario() -> GameState:
    """Create a symmetric open-play midgame scenario for comparing the 4 search configurations."""
    state = GameState.create_default_map()
    state.apply_action("MOVE_LEFT")
    state.apply_action("MOVE_LEFT")
    return state


def run_four_configurations_experiment(depths=None) -> list:
    if depths is None:
        depths = [2, 3, 4, 5]

    configs = [
        ("Minimax Search", False, False),
        ("Alpha-Beta Search", True, False),
        ("Heuristic Minimax Search", False, True),
        ("Heuristic Minimax with Alpha-Beta", True, True),
    ]

    results = []
    print(f"{'Configuration':<35} | {'Depth':>5} | {'Explored States':>16} | {'Time (s)':>12} | {'Action':<10}")
    print("-" * 88)

    for depth in depths:
        for name, use_ab, use_h in configs:
            scenario = create_midgame_scenario()
            agent = MinimaxAgent(
                player_id=1,
                depth=depth,
                use_alpha_beta=use_ab,
                use_heuristic=use_h,
                name=name,
            )
            action = agent.get_action(scenario)
            row = {
                "config": name,
                "depth": depth,
                "explored_states": agent.explored_states,
                "time": agent.last_decision_time,
                "action": action,
            }
            results.append(row)
            print(
                f"{name:<35} | {depth:>5} | {agent.explored_states:>16} | "
                f"{agent.last_decision_time:>12.6f} | {action:<10}"
            )
        print("-" * 88)

    return results


def simulate_match(agent1, agent2, max_turns: int = 80) -> dict:
    state = GameState.create_default_map()
    state.max_turns = max_turns
    agent1.reset_metrics()
    agent2.reset_metrics()

    while not state.is_terminal():
        if state.current_player == 1:
            action = agent1.get_action(state)
        else:
            action = agent2.get_action(state)
        state.apply_action(action)

    return {
        "p1_name": agent1.name,
        "p2_name": agent2.name,
        "winner": state.get_winner(),
        "turns": state.turn_count,
        "p1_hp": state.tanks[1].hp,
        "p1_base_hp": state.bases[1].hp,
        "p2_hp": state.tanks[2].hp,
        "p2_base_hp": state.bases[2].hp,
        "p1_avg_time": agent1.total_decision_time / max(1, agent1.decisions_count),
        "p1_avg_states": agent1.total_explored_states / max(1, agent1.decisions_count),
        "p2_avg_time": agent2.total_decision_time / max(1, agent2.decisions_count),
        "p2_avg_states": agent2.total_explored_states / max(1, agent2.decisions_count),
    }


def main():
    parser = argparse.ArgumentParser(description="Task 2: Tank Battle Game")
    parser.add_argument("--experiment", action="store_true", help="Run benchmark comparing the 4 configurations")
    parser.add_argument("--ext-p2", type=str, default=None, help="Path to external Python file for Player 2 agent")
    parser.add_argument("--ext-class", type=str, default="CustomAgent", help="Class name of external agent")
    args = parser.parse_args()

    if args.experiment:
        run_four_configurations_experiment([2, 3, 4, 5])
    else:
        from ui.pygame_ui import TankBattleUI

        ui = TankBattleUI()
        if args.ext_p2:
            ui.import_external_agent(2, args.ext_p2, args.ext_class)
        ui.run()


if __name__ == "__main__":
    main()
