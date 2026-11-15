import unittest
from task3.kakuro_csp import BOARDS, KakuroCSP
from task3.solver import KakuroSolver
class KakuroTests(unittest.TestCase):
    def check_board(self, name, size, white_cells):
        board = BOARDS[name]
        csp = KakuroCSP(board)
        solver = KakuroSolver(csp)
        self.assertEqual([len(row) for row in board], [size] * size)
        self.assertEqual(len(csp.variables), white_cells)
        self.assertTrue(all(domain == set(range(1, 10)) for domain in csp.domains.values()))
        solution = solver.solve()
        self.assertIsNotNone(solution)
        self.assertTrue(csp.is_valid_solution(solution))
        self.assertEqual(len(solver.processed), white_cells)
        self.assert_search_counts(solver, 0, 0, 1)

        # Kiểm tra trực tiếp trên bàn, độc lập với danh sách dãy của CSP.
        for r, row in enumerate(board):
            for c, clue in enumerate(row):
                if not isinstance(clue, tuple):
                    continue
                across, down = clue
                for total, neighbors in [
                    (across, [(r, j) for j in range(c + 1, size)]),
                    (down, [(i, c) for i in range(r + 1, size)]),
                ]:
                    if not total:
                        continue
                    digits = []
                    for cell in neighbors:
                        if cell not in solution:
                            break
                        digits.append(solution[cell])
                    self.assertEqual(sum(digits), total)
                    self.assertEqual(len(digits), len(set(digits)))
        self.assertEqual(solver.solve(), solution)

    def test_simple(self):
        self.check_board("simple", 5, 12)

    def test_advanced(self):
        self.check_board("advanced", 9, 48)

    def test_unsatisfiable(self):
        solver = KakuroSolver(KakuroCSP([
            ["#", (0, 1)],
            [(2, 0), None],
        ]))
        self.assertIsNone(solver.solve())
        self.assertTrue(any(not changes[cell] for _, cell, changes, _ in solver.steps))
        self.assert_search_counts(solver, 0, 0, 0)

    def assert_search_counts(self, solver, expanded, depth, active):
        self.assertEqual(solver.nodes_expanded, expanded)
        self.assertEqual(solver.max_search_depth, depth)
        self.assertEqual(solver.peak_active_nodes, active)

    def test_search_counts_with_backtracking_and_reset(self):
        csp = KakuroCSP(BOARDS["backtracking_demo"])
        solver = KakuroSolver(csp)
        for _ in range(2):
            self.assertTrue(csp.is_valid_solution(solver.solve()))
            self.assertEqual(solver.backtracks, 1)
            # Có 4 lần gán, nhưng một nhánh bị loại trước khi gọi đệ quy.
            self.assertEqual(sum(event[0] == "assign" for event in solver.steps), 4)
            self.assert_search_counts(solver, 3, 3, 4)

    def test_duplicate_digits_with_correct_sums(self):
        csp = KakuroCSP([
            ["#", (0, 4), (0, 4)],
            [(4, 0), None, None],
            [(4, 0), None, None],
        ])
        self.assertFalse(csp.is_valid_solution(dict.fromkeys(csp.variables, 2)))

    def test_backtracking_replay(self):
        # Bàn kiểm thử riêng có nhánh MRV đầu tiên thất bại.
        csp = KakuroCSP([
            ["#", (0, 8), (0, 17), (0, 14)],
            [(14, 0), None, None, None],
            [(13, 0), None, None, None],
            [(12, 0), None, None, None],
        ])
        solver = KakuroSolver(csp)
        solution = solver.solve()
        self.assertIsNotNone(solution)
        self.assertGreater(solver.backtracks, 0)
        domains = csp.domains.copy()
        for action, cell, changes, _ in solver.steps:
            if action == "backtrack":
                self.assertTrue(all(values >= domains[item] for item, values in changes.items()))
                self.assertGreater(len(changes[cell]), 1)
            domains.update(changes)
        self.assertEqual(domains, {cell: {value} for cell, value in solution.items()})
