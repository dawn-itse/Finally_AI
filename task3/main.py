import argparse

if __package__:
    from .kakuro_csp import BOARDS, KakuroCSP
    from .solver import KakuroSolver
else:
    from kakuro_csp import BOARDS, KakuroCSP
    from solver import KakuroSolver


def main():
    parser = argparse.ArgumentParser(description="Task 3 - Kakuro CSP")
    parser.add_argument("--board", choices=BOARDS, default="simple")
    parser.add_argument("--no-ui", action="store_true")
    args = parser.parse_args()

    csp = KakuroCSP(BOARDS[args.board])
    solver = KakuroSolver(csp)
    if args.no_ui:
        solution = solver.solve()
        print("Solved" if solution is not None else "No solution")
        if solution is not None:
            for row, line in enumerate(csp.board_data):
                print(" ".join(str(solution.get((row, col), "#")) for col in range(len(line))))
    else:
        if __package__:
            from .ui import KakuroUI
        else:
            from ui import KakuroUI
        KakuroUI(csp, solver).run()

    print(f"Time: {solver.elapsed * 1000:.3f} ms | "
          f"Backtracks: {solver.backtracks} | Variables processed: {len(solver.processed)}")


if __name__ == "__main__":
    main()
