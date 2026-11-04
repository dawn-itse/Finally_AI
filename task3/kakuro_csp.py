class KakuroCSP:
    def __init__(self, board_data):
        self.board_data = board_data
        self.variables = []
        self.domains = {}
        self.constraints = []
