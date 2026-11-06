DIRECTION_DELTAS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

ACTION_TO_DIRECTION = {
    "MOVE_UP": "UP",
    "MOVE_DOWN": "DOWN",
    "MOVE_LEFT": "LEFT",
    "MOVE_RIGHT": "RIGHT",
}


class Entity:
    def __init__(self, x: int, y: int, hp: int):
        self.x = x
        self.y = y
        self.hp = hp

    def take_damage(self, damage: int = 1):
        self.hp = max(0, self.hp - damage)

    def is_alive(self) -> bool:
        return self.hp > 0


class Tank(Entity):
    INITIAL_HP = 6
    ACTIONS = ["MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT", "FIRE", "STAY"]

    def __init__(self, x: int, y: int, direction: str = "UP", player_id: int = 1, hp: int = INITIAL_HP):
        super().__init__(x, y, hp)
        self.direction = direction
        self.player_id = player_id

    def clone(self):
        return Tank(self.x, self.y, self.direction, self.player_id, self.hp)


class Base(Entity):
    INITIAL_HP = 9

    def __init__(self, x: int, y: int, player_id: int = 1, hp: int = INITIAL_HP):
        super().__init__(x, y, hp)
        self.player_id = player_id

    def clone(self):
        return Base(self.x, self.y, self.player_id, self.hp)


class Wall(Entity):
    INITIAL_HP = 3

    def __init__(self, x: int, y: int, hp: int = INITIAL_HP):
        super().__init__(x, y, hp)

    def clone(self):
        return Wall(self.x, self.y, self.hp)


class Bullet:
    SPEED = 3
    DAMAGE = 1

    def __init__(self, x: int, y: int, direction: str, owner_id: int, active: bool = True):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner_id = owner_id
        self.active = active

    def clone(self):
        return Bullet(self.x, self.y, self.direction, self.owner_id, self.active)
