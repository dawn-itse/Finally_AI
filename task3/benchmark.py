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

    print("Board | Runs | Mean ms | SD ms | Mean backtracks | Mean variables | Mean peak KiB")
    for name in BOARDS:
        runs = [row for row in rows if row["board"] == name]
        times = [row["time_ms"] for row in runs]
        backtracks = statistics.mean(row["backtracks"] for row in runs)
        variables = statistics.mean(row["variables_processed"] for row in runs)
        peak = statistics.mean(row["peak_bytes"] for row in runs) / 1024
        print(f"{name} | {len(runs)} | {statistics.mean(times):.3f} | "
              f"{statistics.stdev(times):.3f} | {backtracks:g} | {variables:g} | {peak:.2f}")
    print(path)


if __name__ == "__main__":
    run_benchmark()
