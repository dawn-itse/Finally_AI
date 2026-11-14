# None là ô trắng, # là ô đen, (ngang, dọc) là ô gợi ý.
BOARDS = {
    "simple": [
        ["#", "#", (0, 21), (0, 14), "#"],
        ["#", (12, 14), None, None, (0, 11)],
        [(21, 0), None, None, None, None],
        [(11, 0), None, None, None, None],
        ["#", (16, 0), None, None, "#"],
    ],
    "advanced": [
        ["#", "#", (0, 44), (0, 16), (0, 9), "#", (0, 15), (0, 44), "#"],
        ["#", (22, 0), None, None, None, (3, 11), None, None, (0, 14)],
        ["#", (28, 17), None, None, None, None, None, None, None],
        [(14, 0), None, None, "#", (20, 12), None, None, None, None],
        [(17, 0), None, None, (22, 29), None, None, None, None, (0, 7)],
        ["#", (28, 12), None, None, None, None, (12, 0), None, None],
        [(14, 0), None, None, None, None, (0, 7), (6, 12), None, None],
        [(39, 0), None, None, None, None, None, None, None, "#"],
        ["#", (16, 0), None, None, (8, 0), None, None, None, "#"],
    ],
    "backtracking_demo": [
    ["#", (0, 8), (0, 17), (0, 14)],
    [(14, 0), None, None, None],
    [(13, 0), None, None, None],
    [(12, 0), None, None, None],
],
}


class KakuroCSP:
    def __init__(self, board_data):
        self.board_data = board_data
        self.variables = [
            (row, col)
            for row, line in enumerate(board_data)
            for col, cell in enumerate(line)
            if cell is None
        ]
        self.domains = {cell: set(range(1, 10)) for cell in self.variables}
        self.constraints = []
        self.cell_constraints = {cell: [] for cell in self.variables}

        # Mỗi gợi ý tạo một ràng buộc tổng và không trùng số.
        for row, line in enumerate(board_data):
            for col, clue in enumerate(line):
                if not isinstance(clue, tuple):
                    continue
                for total, (dr, dc) in zip(clue, ((0, 1), (1, 0))):
                    if not total:
                        continue
                    cells = []
                    r, c = row + dr, col + dc
                    while (r, c) in self.domains:
                        cells.append((r, c))
                        r, c = r + dr, c + dc
                    index = len(self.constraints)
                    self.constraints.append((tuple(cells), total))
                    for cell in cells:
                        self.cell_constraints[cell].append(index)

    def is_valid_solution(self, assignment):
        if assignment.keys() != self.domains.keys():
            return False
        if any(value not in self.domains[cell] for cell, value in assignment.items()):
            return False
        for cells, total in self.constraints:
            digits = [assignment[cell] for cell in cells]
            if sum(digits) != total or len(set(digits)) != len(digits):
                return False
        return True
