import csv
import statistics
import tracemalloc
from pathlib import Path
from time import perf_counter

from .kakuro_csp import BOARDS, KakuroCSP
from .solver import KakuroSolver


def run_benchmark():
    rows = []
    for name, board in BOARDS.items():
        csp = KakuroCSP(board)
        for trial in range(1, 21):
            solver = KakuroSolver(csp)
            start = perf_counter()
            solution = solver.solve()
            elapsed = perf_counter() - start
            if solution is None or not csp.is_valid_solution(solution):
                raise RuntimeError(f"Nghiệm không hợp lệ: {name}, lượt {trial}")

            # Đo riêng bộ nhớ, bao gồm nhật ký nhưng không gồm UI.
            memory_solver = KakuroSolver(csp)
            tracemalloc.start()
            try:
                measured = memory_solver.solve()
                _, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            if measured != solution:
                raise RuntimeError(f"Kết quả không tái lập: {name}, lượt {trial}")
            rows.append({
                "board": name,
                "trial": trial,
                "time_ms": elapsed * 1000,
                "backtracks": solver.backtracks,
                "variables_processed": len(solver.processed),
                "peak_bytes": peak,
                "nodes_expanded": solver.nodes_expanded,
                "max_search_depth": solver.max_search_depth,
                "peak_active_nodes": solver.peak_active_nodes,
            })

    # Tạo file mới để giữ các lần đo trước.
    path = Path(__file__).with_name("benchmark_results.csv")
    if path.exists():
        from datetime import datetime

        path = path.with_stem(f"{path.stem}_{datetime.now():%Y%m%d_%H%M%S}")
    with path.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("\nExecution and memory")
    header = (f"{'Board':<18} {'Runs':>4} {'Avg ms':>10} {'SD ms':>9} "
              f"{'Peak KiB*':>10} {'Backtracks*':>11} {'Vars*':>6}")
    print(header)
    print("-" * len(header))
    for name in BOARDS:
        runs = [row for row in rows if row["board"] == name]
        times = [row["time_ms"] for row in runs]
        backtracks = statistics.mean(row["backtracks"] for row in runs)
        variables = statistics.mean(row["variables_processed"] for row in runs)
        peak = statistics.mean(row["peak_bytes"] for row in runs) / 1024
        print(f"{name:<18} {len(runs):>4} {statistics.mean(times):>10.3f} "
              f"{statistics.stdev(times):>9.3f} {peak:>10.2f} "
              f"{backtracks:>11g} {variables:>6g}")

    print("\nSearch tree")
    header = (f"{'Board':<18} {'Expanded*':>10} {'Max depth':>10} "
              f"{'Peak active':>11}")
    print(header)
    print("-" * len(header))
    for name in BOARDS:
        runs = [row for row in rows if row["board"] == name]
        expanded = statistics.mean(row["nodes_expanded"] for row in runs)
        depth = max(row["max_search_depth"] for row in runs)
        active = max(row["peak_active_nodes"] for row in runs)
        print(f"{name:<18} {expanded:>10g} {depth:>10} {active:>11}")

    print("\n* Mean over runs. Expanded and Peak active are counts in nodes.")
    print(f"CSV: {path}")


if __name__ == "__main__":
    run_benchmark()
