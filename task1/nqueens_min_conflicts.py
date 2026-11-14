"""Giải N-Queens bằng hai biến thể Min-Conflicts đơn giản."""

import random
import time


class NQueensMinConflicts:
    """Mỗi hàng có một hậu; state[row] là cột của hậu ở hàng đó."""

    def __init__(self, n: int, max_steps: int = 10000, seed: int | None = None):
        if n < 1:
            raise ValueError("N phải lớn hơn hoặc bằng 1.")
        if max_steps < 0:
            raise ValueError("max_steps không được âm.")

        self.n = n
        self.max_steps = max_steps
        self.seed = seed
        self.random = random.Random(seed)

    def initialize_state(self) -> list[int]:
        """Tạo trạng thái ngẫu nhiên với đúng một hậu trên mỗi hàng."""
        return [self.random.randrange(self.n) for _ in range(self.n)]

    @staticmethod
    def _validate_state(state: list[int]) -> None:
        if not state:
            raise ValueError("Trạng thái không được rỗng.")
        n = len(state)
        if any(not isinstance(col, int) or col < 0 or col >= n for col in state):
            raise ValueError("Mỗi cột phải là số nguyên trong khoảng 0 đến N-1.")

    def count_conflicts(self, state: list[int], row: int) -> int:
        """Đếm các hậu khác đang ăn hậu ở hàng row."""
        self._validate_state(state)
        if not 0 <= row < len(state):
            raise IndexError("Chỉ số hàng nằm ngoài bàn cờ.")

        return self._count_conflicts_unchecked(state, row)

    @staticmethod
    def _count_conflicts_unchecked(state: list[int], row: int) -> int:
        """Đếm conflict nội bộ sau khi trạng thái đã được kiểm tra."""

        conflicts = 0
        for other_row in range(len(state)):
            if other_row == row:
                continue
            same_column = state[row] == state[other_row]
            same_diagonal = abs(row - other_row) == abs(state[row] - state[other_row])
            if same_column or same_diagonal:
                conflicts += 1
        return conflicts

    def is_solution(self, state: list[int]) -> bool:
        """Trả về True nếu trạng thái chứa N hậu không ăn nhau."""
        if len(state) != self.n:
            return False
        try:
            self._validate_state(state)
        except (TypeError, ValueError):
            return False
        return all(self._count_conflicts_unchecked(state, row) == 0 for row in range(self.n))

    def to_board(self, state: list[int]) -> list[list[int]]:
        """Chuyển state một chiều thành ma trận 0/1 như NQueensCNF."""
        self._validate_state(state)
        if len(state) != self.n:
            raise ValueError("Độ dài state phải bằng N.")
        board = [[0 for _ in range(self.n)] for _ in range(self.n)]
        for row, col in enumerate(state):
            board[row][col] = 1
        return board

    def _get_result(self, method: str, success: bool, state: list[int], steps: int, elapsed: float) -> dict:
        return {
            "n": self.n,
            "method": method,
            "success": success,
            "satisfiable": success,
            "state": state.copy() if success else None,
            "board": self.to_board(state) if success else None,
            "steps": steps,
            "solver_time": elapsed,
            "total_time": elapsed,
            "seed": self.seed,
        }

    def _solve(self, improved: bool) -> dict:
        method = "improved" if improved else "standard"
        start_time = time.perf_counter()

        # Hai hậu không thể đặt an toàn trên 2 hoặc 3 hàng.
        if self.n in (2, 3):
            return self._get_result(method, False, [], 0, time.perf_counter() - start_time)

        state = self.initialize_state()
        steps = 0
        while not self.is_solution(state) and steps < self.max_steps:
            conflict_counts = [self._count_conflicts_unchecked(state, row) for row in range(self.n)]
            conflicted_rows = [row for row, count in enumerate(conflict_counts) if count > 0]
            if not conflicted_rows:
                break

            if improved:
                highest_conflict = max(conflict_counts[row] for row in conflicted_rows)
                candidate_rows = [row for row in conflicted_rows if conflict_counts[row] == highest_conflict]
            else:
                candidate_rows = conflicted_rows
            row = self.random.choice(candidate_rows)

            # Min-Conflicts: thử từng cột và tính số xung đột nếu đặt hậu vào đó.
            # Chọn cột có ít xung đột nhất. Nếu có nhiều cột tốt như nhau thì chọn ngẫu nhiên
            # để tránh bị kẹt mãi ở cùng một lựa chọn (tránh dao động cục bộ).
            column_scores = []
            for col in range(self.n):
                if col == state[row]:
                    continue
                state[row] = col
                score = self._count_conflicts_unchecked(state, row)
                column_scores.append((col, score))
            best_score = min(score for _, score in column_scores)
            best_columns = [col for col, score in column_scores if score == best_score]
            state[row] = self.random.choice(best_columns)
            steps += 1

        success = self.is_solution(state)
        return self._get_result(method, success, state, steps, time.perf_counter() - start_time)

    def solve_standard(self) -> dict:
        """
        Min-Conflicts tiêu chuẩn: mỗi bước chọn ngẫu nhiên một hậu đang có xung đột,
        sau đó di chuyển hậu đó đến cột có ít xung đột nhất.
        Trả về dict gồm: success, state, board, steps, solver_time, ...
        """
        return self._solve(improved=False)

    def solve_heuristic(self) -> dict:
        """
        Min-Conflicts cải tiến (heuristic): mỗi bước ưu tiên chọn hậu có NHIỀU xung đột nhất
        (thay vì chọn ngẫu nhiên như phiên bản Standard). Nếu có nhiều hậu cùng mức xung đột cao
        thì chọn ngẫu nhiên trong số đó. Mục tiêu: giải quyết điểm nóng trước, giảm bước lặp.
        Trả về dict gồm: success, state, board, steps, solver_time, ...
        """
        return self._solve(improved=True)
