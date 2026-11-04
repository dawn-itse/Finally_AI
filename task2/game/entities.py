class Entity:
    def __init__(self, x: int, y: int, hp: int):
        self.x = x
        self.y = y
        self.hp = hp


class Tank(Entity):
    INITIAL_HP = 6
    ACTIONS = ["MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT", "FIRE", "STAY"]

    def __init__(self, x: int, y: int, direction: str = "UP", player_id: int = 1):
        super().__init__(x, y, self.INITIAL_HP)
        self.direction = direction
        self.player_id = player_id


class Base(Entity):
    INITIAL_HP = 9

    def __init__(self, x: int, y: int, player_id: int = 1):
        super().__init__(x, y, self.INITIAL_HP)
        self.player_id = player_id


class Wall(Entity):
    INITIAL_HP = 3

    def __init__(self, x: int, y: int):
        super().__init__(x, y, self.INITIAL_HP)


class Bullet:
    SPEED = 3
    DAMAGE = 1

    def __init__(self, x: int, y: int, direction: str, owner_id: int):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner_id = owner_id
        self.active = True
