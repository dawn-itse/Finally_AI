import time
from pysat.solvers import Glucose3


class NQueensCNF:
    def __init__(self, n: int):
        if n < 4:
            raise ValueError("N must be greater than or equal to 4.")
        self.n = n
        self.clauses = []
        self.solution_board = None
        self.solve_time = 0.0
        self.total_time = 0.0

    def to_var(self, row: int, col: int) -> int:
        return row * self.n + col + 1

    def to_coord(self, var: int) -> tuple:
        idx = abs(var) - 1
        return idx // self.n, idx % self.n

    def generate_clauses(self) -> list:
        self.clauses = []

        # Luật 1 - Mỗi hàng phải có ít nhất một hậu
        for r in range(self.n):
            row_clause = [self.to_var(r, c) for c in range(self.n)]
            self.clauses.append(row_clause)

        # Luật 2 - Không quá 1 hậu trên cùng 1 hàng (Cặp số âm):
        for r in range(self.n):
            for c1 in range(self.n):
                for c2 in range(c1 + 1, self.n):
                    self.clauses.append([-self.to_var(r, c1), -self.to_var(r, c2)])

        # Luật 3 - Không quá 1 hậu trên cùng 1 cột (Cặp số âm):
        for c in range(self.n):
            for r1 in range(self.n):
                for r2 in range(r1 + 1, self.n):
                    self.clauses.append([-self.to_var(r1, c), -self.to_var(r2, c)])

        # Luật 4 - Không quá 1 hậu trên cùng đường chéo (Cặp số âm):
        for r1 in range(self.n):
            for c1 in range(self.n):
                # Down-right
                r2, c2 = r1 + 1, c1 + 1
                while r2 < self.n and c2 < self.n:
                    self.clauses.append([-self.to_var(r1, c1), -self.to_var(r2, c2)])
                    r2 += 1
                    c2 += 1

                # Down-left
                r2, c2 = r1 + 1, c1 - 1
                while r2 < self.n and c2 >= 0:
                    self.clauses.append([-self.to_var(r1, c1), -self.to_var(r2, c2)])
                    r2 += 1
                    c2 -= 1

        return self.clauses

    def solve(self) -> dict:
        start_total = time.perf_counter()

        if not self.clauses:
            self.generate_clauses()

        solver = Glucose3()
        for clause in self.clauses:
            solver.add_clause(clause)

        start_solve = time.perf_counter()
        is_sat = solver.solve()
        self.solve_time = time.perf_counter() - start_solve

        if is_sat:
            model = solver.get_model()
            self.solution_board = [[0 for _ in range(self.n)] for _ in range(self.n)]
            for literal in model:
                if literal > 0:
                    r, c = self.to_coord(literal)
                    self.solution_board[r][c] = 1
        else:
            self.solution_board = None

        solver.delete()
        self.total_time = time.perf_counter() - start_total

        return {
            "n": self.n,
            "satisfiable": is_sat,
            "num_variables": self.n * self.n,
            "num_clauses": len(self.clauses),
            "solver_time": self.solve_time,
            "total_time": self.total_time,
            "board": self.solution_board,
        }

    def format_board(self) -> str:
        if self.solution_board is None:
            return "No solution found."
        lines = []
        for r in range(self.n):
            row_str = " ".join("Q" if self.solution_board[r][c] == 1 else "." for c in range(self.n))
            lines.append(row_str)
        return "\n".join(lines)


def run_experiments(n_values: list) -> list:
    results = []
    print(f"{'N':>5} | {'Variables':>10} | {'CNF Clauses':>14} | {'Solver Time (s)':>16} | {'Total Time (s)':>15}")
    print("-" * 72)
    for n in n_values:
        solver_obj = NQueensCNF(n)
        res = solver_obj.solve()
        results.append(res)
        print(
            f"{res['n']:>5} | {res['num_variables']:>10} | {res['num_clauses']:>14} | "
            f"{res['solver_time']:>16.6f} | {res['total_time']:>15.6f}"
        )
    return results


if __name__ == "__main__":
    example = NQueensCNF(4)
    result = example.solve()
    print(f"Solution for N = {example.n} (Clauses: {result['num_clauses']}, Time: {result['solver_time']:.6f}s):")
    print(example.format_board())
    print("\nRunning experiments for increasing values of N >= 4:")
    run_experiments([4, 8, 12, 16, 20, 25, 30, 40, 50])
