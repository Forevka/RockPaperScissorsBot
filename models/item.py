import typing

from config import game_modes

class GameItem:
    def __init__(self, id: int, name: str, beat: typing.Dict[int, str]):
        self.name: str = name
        self.id: int = id
        self.beat: typing.List[int] = list(beat.keys())
        self.description: typing.Dict[int, str] = beat
    
    def __str__(self):
        return f"Item {self.name} {self.id} {self.beat}"


def get_item(id: int, difficulty: int):
    return GameItem(id, **game_modes[difficulty]["game_items"][id])
