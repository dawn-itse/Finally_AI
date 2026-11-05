from nqueens_cnf import NQueensCNF, run_experiments


def main():
    print("=== Task 1: N-Queens Problem with Propositional Logic (Glucose3) ===")
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
