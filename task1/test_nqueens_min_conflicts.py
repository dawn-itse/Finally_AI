import unittest
from unittest.mock import patch

try:
    from .nqueens_min_conflicts import NQueensMinConflicts
except ImportError:
    from nqueens_min_conflicts import NQueensMinConflicts


class TestNQueensMinConflicts(unittest.TestCase):
    def test_random_state_has_one_queen_per_row_and_repeats_with_seed(self):
        first = NQueensMinConflicts(8, seed=19).initialize_state()
        second = NQueensMinConflicts(8, seed=19).initialize_state()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 8)
        self.assertTrue(all(0 <= col < 8 for col in first))

    def test_conflicts_in_same_column_and_diagonal(self):
        solver = NQueensMinConflicts(4)
        self.assertEqual(solver.count_conflicts([0, 0, 3, 1], 0), 1)
        self.assertEqual(solver.count_conflicts([0, 2, 1, 3], 0), 1)

    def test_solution_validation(self):
        solver = NQueensMinConflicts(4)
        self.assertTrue(solver.is_solution([1, 3, 0, 2]))
        self.assertFalse(solver.is_solution([0, 0, 3, 1]))
        self.assertFalse(solver.is_solution([0, 2, 1, 3]))
        self.assertFalse(solver.is_solution([0, 1]))
        self.assertFalse(solver.is_solution([0, 1, 2, 4]))

    def test_state_converts_to_cnf_compatible_board(self):
        solver = NQueensMinConflicts(4)
        expected = [
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
            [0, 0, 1, 0],
        ]
        self.assertEqual(solver.to_board([1, 3, 0, 2]), expected)
        self.assertTrue(all(sum(row) == 1 for row in expected))

    def test_small_board_edge_cases(self):
        self.assertTrue(NQueensMinConflicts(1, seed=2).solve_standard()["success"])
        for n in (2, 3):
            self.assertFalse(NQueensMinConflicts(n, seed=2).solve_standard()["success"])
            self.assertFalse(NQueensMinConflicts(n, seed=2).solve_heuristic()["success"])

    def test_step_limit_and_both_algorithms(self):
        for method in ("solve_standard", "solve_heuristic"):
            capped = getattr(NQueensMinConflicts(4, max_steps=0, seed=3), method)()
            self.assertFalse(capped["success"])
            self.assertEqual(capped["steps"], 0)

            result = getattr(NQueensMinConflicts(8, max_steps=10000, seed=42), method)()
            self.assertTrue(result["success"])
            self.assertTrue(NQueensMinConflicts(8).is_solution(result["state"]))
            self.assertEqual(len(result["board"]), 8)

    def test_constructor_rejects_invalid_limits(self):
        with self.assertRaises(ValueError):
            NQueensMinConflicts(0)
        with self.assertRaises(ValueError):
            NQueensMinConflicts(4, max_steps=-1)

    def test_scores_every_column_except_original(self):
        for original, other_columns in ((0, [1, 2, 3]), (2, [0, 1, 3])):
            for method in ("solve_standard", "solve_heuristic"):
                with self.subTest(original=original, method=method):
                    solver = NQueensMinConflicts(4, max_steps=1, seed=42)
                    state = [original, 3, 0, 2]
                    offered = []

                    def choose(options):
                        offered.append(list(options))
                        return options[0]

                    with patch.object(solver, "initialize_state", return_value=state), \
                         patch.object(solver, "is_solution", return_value=False), \
                         patch.object(solver, "_count_conflicts_unchecked", return_value=1), \
                         patch.object(solver.random, "choice", side_effect=choose):
                        getattr(solver, method)()
                    self.assertEqual(offered[-1], other_columns)

    def test_solver_repeats_result_with_seed(self):
        for method in ("solve_standard", "solve_heuristic"):
            first, second = [
                getattr(NQueensMinConflicts(8, seed=42), method)()
                for _ in range(2)
            ]
            self.assertTrue(first["success"])
            self.assertTrue(NQueensMinConflicts(8).is_solution(first["state"]))
            for key in ("state", "board", "steps"):
                self.assertEqual(first[key], second[key])


if __name__ == "__main__":
    unittest.main()
