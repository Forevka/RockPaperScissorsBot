import enum
from item import GameItemMeta

class GameResult(enum.IntEnum):
    DEFEAT: int = 0
    WIN: int = 1
    DRAW: int = 2

    def __init__(self, first: GameItemMeta, second: GameItemMeta):
