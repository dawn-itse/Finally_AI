from collections import deque
from itertools import combinations, permutations
from time import perf_counter


class KakuroSolver:
    def __init__(self, csp):
        self.csp = csp

    def solve(self):
        start = perf_counter()
        self.steps = []
        self.backtracks = 0
        self.processed = set()
        domains = self.csp.domains.copy()
        # Chỉ giữ các bộ số thỏa tổng và không trùng trong từng dãy.
        self.options = [
            [order for digits in combinations(range(1, 10), len(cells))
             if sum(digits) == total for order in permutations(digits)]
            for cells, total in self.csp.constraints
        ]
        self.solution = None
        if self._propagate(domains, range(len(self.options))):
            self.solution = self._search(domains)
        self.elapsed = perf_counter() - start
        return self.solution

    def _propagate(self, domains, indices):
        # Forward Checking kiểm tra các dãy bị ảnh hưởng sau khi gán.
        # Đưa dãy giao nhau vào hàng đợi để lan truyền miền vừa thu hẹp.
        pending = deque(indices)
        while pending:
            index = pending.popleft()
            cells, total = self.csp.constraints[index]
            supported = [set() for cell in cells]
            self.processed.update(cells)
            for order in self.options[index]:
                if all(value in domains[cell] for cell, value in zip(cells, order)):
                    for values, value in zip(supported, order):
                        values.add(value)
            for cell, values in zip(cells, supported):
                if values != domains[cell]:
                    removed = domains[cell] - values
                    domains[cell] = values
                    self.steps.append(("prune", cell, {cell: values},
                                       f"Sum {total}: remove {sorted(removed)}"))
                    if not values:
                        return False
                    for neighbor in self.csp.cell_constraints[cell]:
                        if neighbor != index and neighbor not in pending:
                            pending.append(neighbor)
            if not cells and total:
                return False
        return True

    def _search(self, domains):
        # MRV chọn ô chưa cố định có ít giá trị nhất.
        undecided = [cell for cell in domains if len(domains[cell]) > 1]
        if not undecided:
            assignment = {cell: next(iter(values)) for cell, values in domains.items()}
            return assignment if self.csp.is_valid_solution(assignment) else None

        cell = min(undecided, key=lambda item: len(domains[item]))
        self.processed.add(cell)
        for value in sorted(domains[cell]):
            branch = domains.copy()
            branch[cell] = {value}
            self.steps.append(("assign", cell, {cell: {value}}, f"MRV: try {value}"))
            if self._propagate(branch, self.csp.cell_constraints[cell]):
                solution = self._search(branch)
                if solution is not None:
                    return solution

            self.backtracks += 1
            restored = {item: values for item, values in domains.items()
                        if branch[item] != values}
            self.steps.append(("backtrack", cell, restored, f"Undo {value}"))
        return None
