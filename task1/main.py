from nqueens_cnf import NQueensCNF, run_experiments
from nqueens_min_conflicts import NQueensMinConflicts


def main():
    print("=== Task 1 Part 1: N-Queens with Min-Conflicts Local Search ===")
    mc_solver = NQueensMinConflicts(n=8, max_steps=5000, seed=42)
    res_std = mc_solver.solve_standard()
    res_heur = mc_solver.solve_heuristic()
    print(f"Standard Min-Conflicts (N=8): success={res_std['success']}, steps={res_std['steps']}, time={res_std['solver_time']:.6f}s")
    print(f"Heuristic Min-Conflicts (N=8): success={res_heur['success']}, steps={res_heur['steps']}, time={res_heur['solver_time']:.6f}s\n")

    print("=== Task 1 Part 2: N-Queens Problem with Propositional Logic (Glucose3) ===")
    n_demo = 8
    solver = NQueensCNF(n_demo)
    res = solver.solve()
    print(f"\nBoard size N = {n_demo}")
    print(f"Total variables: {res['num_variables']}")
    print(f"Total CNF clauses: {res['num_clauses']}")
    print(f"Solver running time: {res['solver_time']:.6f} seconds")
    print("\nSolution board:")
    print(solver.format_board())

    print("\n=== Experiment with increasing values of N (N >= 4) ===")
    n_values = [4, 8, 12, 16, 20, 25, 30, 40, 50]
    run_experiments(n_values)


if __name__ == "__main__":
    main()
