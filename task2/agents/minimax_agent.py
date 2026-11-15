import heapq
import math
import time
from agents.base_agent import BaseAgent
from game.entities import ACTION_TO_DIRECTION, DIRECTION_DELTAS


class MinimaxAgent(BaseAgent):
    CONFIG_MINIMAX = "Minimax Search"
    CONFIG_ALPHA_BETA = "Alpha-Beta Search"
    CONFIG_H_MINIMAX = "Heuristic Minimax Search"
    CONFIG_H_ALPHA_BETA = "Heuristic Minimax with Alpha-Beta"

    def __init__(
        self,
        player_id: int,
        depth: int = 4,
        use_alpha_beta: bool = True,
        use_heuristic: bool = True,
        name: str = None,
    ):
        if name is None:
            if use_heuristic and use_alpha_beta:
                name = self.CONFIG_H_ALPHA_BETA
            elif use_heuristic and not use_alpha_beta:
                name = self.CONFIG_H_MINIMAX
            elif not use_heuristic and use_alpha_beta:
                name = self.CONFIG_ALPHA_BETA
            else:
                name = self.CONFIG_MINIMAX

        super().__init__(player_id, name=name)
        self.depth = depth
        self.use_alpha_beta = use_alpha_beta
        self.use_heuristic = use_heuristic
        self.opponent_id = 2 if player_id == 1 else 1

        # Performance metrics for experiments
        self.explored_states = 0
        self.last_decision_time = 0.0
        self.total_decision_time = 0.0
        self.total_explored_states = 0
        self.decisions_count = 0

    def reset_metrics(self):
        self.explored_states = 0
        self.last_decision_time = 0.0
        self.total_decision_time = 0.0
        self.total_explored_states = 0
        self.decisions_count = 0

    def get_action(self, state) -> str:
        start_time = time.perf_counter()
        self.explored_states = 0

        legal_actions = state.get_legal_actions(self.player_id)
        if not legal_actions:
            return "STAY"

        ordered_actions = self._order_actions(state, legal_actions, self.player_id)
        best_action = ordered_actions[0]
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf

        for action in ordered_actions:
            next_state = state.get_next_state(action)
            if self.use_alpha_beta:
                score = self._min_value_ab(next_state, self.depth - 1, alpha, beta)
                alpha = max(alpha, score)
            else:
                score = self._min_value(next_state, self.depth - 1)

            if score > best_score:
                best_score = score
                best_action = action

        elapsed = time.perf_counter() - start_time
        self.last_decision_time = elapsed
        self.total_decision_time += elapsed
        self.total_explored_states += self.explored_states
        self.decisions_count += 1
        return best_action

    # --- Standard Minimax (No Alpha-Beta Pruning) ---
    def _max_value(self, state, depth: int) -> float:
        self.explored_states += 1
        if self._cutoff_test(state, depth):
            return self._eval_or_utility(state)

        v = -math.inf
        actions = self._order_actions(state, state.get_legal_actions(self.player_id), self.player_id)
        for action in actions:
            next_state = state.get_next_state(action)
            v = max(v, self._min_value(next_state, depth - 1))
        return v

    def _min_value(self, state, depth: int) -> float:
        self.explored_states += 1
        if self._cutoff_test(state, depth):
            return self._eval_or_utility(state)

        v = math.inf
        actions = self._order_actions(state, state.get_legal_actions(self.opponent_id), self.opponent_id)
        for action in actions:
            next_state = state.get_next_state(action)
            v = min(v, self._max_value(next_state, depth - 1))
        return v

    # --- Minimax with Alpha-Beta Pruning ---
    def _max_value_ab(self, state, depth: int, alpha: float, beta: float) -> float:
        self.explored_states += 1
        if self._cutoff_test(state, depth):
            return self._eval_or_utility(state)

        v = -math.inf
        actions = self._order_actions(state, state.get_legal_actions(self.player_id), self.player_id)
        for action in actions:
            next_state = state.get_next_state(action)
            v = max(v, self._min_value_ab(next_state, depth - 1, alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def _min_value_ab(self, state, depth: int, alpha: float, beta: float) -> float:
        self.explored_states += 1
        if self._cutoff_test(state, depth):
            return self._eval_or_utility(state)

        v = math.inf
        actions = self._order_actions(state, state.get_legal_actions(self.opponent_id), self.opponent_id)
        for action in actions:
            next_state = state.get_next_state(action)
            v = min(v, self._max_value_ab(next_state, depth - 1, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def _cutoff_test(self, state, depth: int) -> bool:
        return state.is_terminal() or depth <= 0

    def _eval_or_utility(self, state) -> float:
        if state.is_terminal() or not self.use_heuristic:
            return state.get_utility(self.player_id)
        return self.evaluate(state)

    def _order_actions(self, state, actions: list, acting_player: int) -> list:
        if not self.use_heuristic:
            return actions

        tank = state.tanks.get(acting_player)
        enemy_id = 2 if acting_player == 1 else 1
        enemy_tank = state.tanks.get(enemy_id)
        enemy_base = state.bases.get(enemy_id)

        def action_priority(act: str) -> float:
            if tank is None or not tank.is_alive():
                return 0.0
            if act == "FIRE":
                if self._has_line_of_sight(state, tank.x, tank.y, tank.direction, enemy_id):
                    return 100.0
                if self._has_wall_ahead(state, tank.x, tank.y, tank.direction, enemy_id, max_steps=3):
                    return 15.0
                return -18.0
            if act in ACTION_TO_DIRECTION:
                direction = ACTION_TO_DIRECTION[act]
                dx, dy = DIRECTION_DELTAS[direction]
                nx, ny = tank.x + dx, tank.y + dy
                dist_base = abs(nx - enemy_base.x) + abs(ny - enemy_base.y)
                dist_tank = abs(nx - enemy_tank.x) + abs(ny - enemy_tank.y)
                return -0.5 * dist_base - 0.5 * dist_tank
            return -20.0

        return sorted(actions, key=action_priority, reverse=True)

    def _has_wall_ahead(
        self, state, x: int, y: int, direction: str, target_player_id: int, max_steps: int = 3
    ) -> bool:
        dx, dy = DIRECTION_DELTAS[direction]
        enemy_tank = state.tanks[target_player_id]
        enemy_base = state.bases[target_player_id]
        toward_enemy = (
            (enemy_base.x - x) * dx + (enemy_base.y - y) * dy > 0
            or (enemy_tank.x - x) * dx + (enemy_tank.y - y) * dy > 0
        )
        if not toward_enemy:
            return False
        for step in range(1, max_steps + 1):
            cx = x + dx * step
            cy = y + dy * step
            if not state.is_inside(cx, cy):
                return False
            if (cx, cy) in state.walls and state.walls[(cx, cy)].is_alive():
                return True
        return False

    def _unobstructed_tank_dist(self, state, x1: int, y1: int, x2: int, y2: int) -> int:
        if x1 != x2 and y1 != y2:
            return 999
        dist = abs(x1 - x2) + abs(y1 - y2)
        if dist == 0:
            return 0
        dx = 0 if x1 == x2 else (1 if x2 > x1 else -1)
        dy = 0 if y1 == y2 else (1 if y2 > y1 else -1)
        cx, cy = x1 + dx, y1 + dy
        while (cx, cy) != (x2, y2):
            if (cx, cy) in state.walls and state.walls[(cx, cy)].is_alive():
                return 999
            cx += dx
            cy += dy
        return dist

    def _has_line_of_sight(self, state, x: int, y: int, direction: str, target_player_id: int) -> bool:
        dx, dy = DIRECTION_DELTAS[direction]
        cx, cy = x + dx, y + dy
        enemy_tank = state.tanks[target_player_id]
        enemy_base = state.bases[target_player_id]

        while state.is_inside(cx, cy):
            if (cx, cy) in state.walls and state.walls[(cx, cy)].is_alive():
                return False
            if enemy_tank.is_alive() and cx == enemy_tank.x and cy == enemy_tank.y:
                return True
            if enemy_base.is_alive() and cx == enemy_base.x and cy == enemy_base.y:
                return True
            cx += dx
            cy += dy
        return False

    def _bfs_distance(self, state, start_x: int, start_y: int, target_x: int, target_y: int) -> int:
        if start_x == target_x and start_y == target_y:
            return 0
        best_cost = {(start_x, start_y): 0}
        pq = [(0, start_x, start_y)]
        while pq:
            cost, cx, cy = heapq.heappop(pq)
            if cx == target_x and cy == target_y:
                return cost
            if cost > best_cost.get((cx, cy), math.inf):
                continue
            for dx, dy in DIRECTION_DELTAS.values():
                nx, ny = cx + dx, cy + dy
                if not state.is_inside(nx, ny):
                    continue
                step_cost = 1
                if (nx, ny) in state.walls and state.walls[(nx, ny)].is_alive():
                    step_cost += state.walls[(nx, ny)].hp
                new_cost = cost + step_cost
                if new_cost < best_cost.get((nx, ny), math.inf):
                    best_cost[(nx, ny)] = new_cost
                    heapq.heappush(pq, (new_cost, nx, ny))
        return abs(start_x - target_x) + abs(start_y - target_y)

    def _repetition_penalty(self, state, pid: int) -> float:
        hist = state.position_history.get(pid, [])
        if len(hist) < 2:
            return 0.0
        repeats = len(hist) - len(set(hist))
        return 14.0 * repeats

    # EVAL(s) in Lecture 07 (Slide 27-28)
    def evaluate(self, state) -> float:
        if state.is_terminal():
            return state.get_utility(self.player_id)

        my_tank = state.tanks[self.player_id]
        op_tank = state.tanks[self.opponent_id]
        my_base = state.bases[self.player_id]
        op_base = state.bases[self.opponent_id]

        score = 0.0

        # 1. Health difference (Tank HP and Base HP)
        score += 60.0 * (my_tank.hp - op_tank.hp)
        score += 50.0 * (my_base.hp - op_base.hp)

        # 2. Wall-aware shortest path distance (accounts for wall HP breaching cost)
        dist_to_op_base = self._bfs_distance(state, my_tank.x, my_tank.y, op_base.x, op_base.y)
        dist_to_op_tank = self._bfs_distance(state, my_tank.x, my_tank.y, op_tank.x, op_tank.y)
        op_dist_to_my_base = self._bfs_distance(state, op_tank.x, op_tank.y, my_base.x, my_base.y)

        score -= 4.0 * dist_to_op_base
        score -= 2.0 * dist_to_op_tank
        score += 2.5 * op_dist_to_my_base

        # 3. Line of sight, close-quarter corridor threat & directional aiming bonus
        my_aims_op = self._has_line_of_sight(state, my_tank.x, my_tank.y, my_tank.direction, self.opponent_id)
        if my_aims_op:
            score += 25.0

        line_dist = self._unobstructed_tank_dist(state, my_tank.x, my_tank.y, op_tank.x, op_tank.y)

        op_aims_my_tank = False
        odx, ody = DIRECTION_DELTAS[op_tank.direction]
        cx, cy = op_tank.x + odx, op_tank.y + ody
        while state.is_inside(cx, cy):
            if (cx, cy) in state.walls and state.walls[(cx, cy)].is_alive():
                break
            if cx == my_tank.x and cy == my_tank.y:
                op_aims_my_tank = True
                if line_dist <= 3 and my_tank.hp <= 1:
                    score -= 500.0
                else:
                    score -= 20.0
                break
            cx += odx
            cy += ody

        if line_dist <= 3:
            if my_tank.hp < op_tank.hp:
                score -= 40.0
            elif op_tank.hp < my_tank.hp:
                score += 40.0
            else:
                mdx_t, mdy_t = DIRECTION_DELTAS[my_tank.direction]
                my_faces_op_tank = (op_tank.x - my_tank.x) * mdx_t + (op_tank.y - my_tank.y) * mdy_t > 0
                if not my_faces_op_tank and not op_aims_my_tank:
                    score -= 15.0

        tank_manhattan = abs(my_tank.x - op_tank.x) + abs(my_tank.y - op_tank.y)
        if tank_manhattan <= 2:
            if my_tank.hp < op_tank.hp:
                score -= 10.0 * (3 - tank_manhattan)
            elif op_tank.hp < my_tank.hp:
                score += 10.0 * (3 - tank_manhattan)

        mdx, mdy = DIRECTION_DELTAS[my_tank.direction]
        if (op_tank.x - my_tank.x) * mdx + (op_tank.y - my_tank.y) * mdy > 0:
            score += 3.0
        if (op_base.x - my_tank.x) * mdx + (op_base.y - my_tank.y) * mdy > 0 or dist_to_op_base <= 1:
            score += 3.0

        # 4. Anti-repetition & anti-stalling penalty
        score -= self._repetition_penalty(state, self.player_id)
        score += self._repetition_penalty(state, self.opponent_id)

        # 5. Active bullet trajectory lookahead (trace until first obstacle or target)
        for bullet in state.bullets:
            if not bullet.active:
                continue
            bdx, bdy = DIRECTION_DELTAS[bullet.direction]
            step = 1
            while True:
                bx = bullet.x + bdx * step
                by = bullet.y + bdy * step
                if not state.is_inside(bx, by):
                    break
                if (bx, by) in state.walls and state.walls[(bx, by)].is_alive():
                    break
                if my_tank.is_alive() and bx == my_tank.x and by == my_tank.y:
                    if step <= 3:
                        score -= 45.0
                    break
                if my_base.is_alive() and bx == my_base.x and by == my_base.y:
                    score -= 45.0
                    break
                if op_tank.is_alive() and bx == op_tank.x and by == op_tank.y:
                    if step <= 3:
                        score += 45.0
                    break
                if op_base.is_alive() and bx == op_base.x and by == op_base.y:
                    score += 45.0
                    break
                step += 1

        return score
