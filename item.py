import random
import typing
import enum

class GameItemMeta:
    def __init__(self, id: int, name: str, beat: typing.Dict[int, str]):
        self.name: str = name
        self.id: int = id
        self.beat: typing.List[int] = list(beat.keys())
        self.description: typing.Dict[int, str] = beat
    
    def __str__(self):
        return f"Item {self.name} {self.id} {self.beat}"
    

class GameResult:
    DEFEAT: int = 0
    WIN: int = 1
    DRAW: int = 2

    def __init__(self, first: GameItemMeta, second: GameItemMeta):
        print(f"fight {first} vs {second}")
        self.winner = first if second.id in first.beat else (second if first.id in second.beat else None)
        self.defeated = None if self.winner is None else (second if self.winner.id not in second.beat else first)
    
    def __str__(self):
        return f"Result: Winner {self.winner} Defeated {self.defeated}"

game_items_normal = {
    1: {"name": "Scissors", "beat": {2: "Scissors cuts paper", 5: "Scissors decapitates lizard"}},
    3: {"name": "Rock", "beat": {1: "Rock crushes scissors", 5: "Rock crushes lizard"}},
    2: {"name": "Paper", "beat": {3: "Paper covers rock", 4: "Paper disproves Spock"}},
    4: {"name": "Spock", "beat": {1: "Spock smashes scissors", 3: "Spock vaporizes rock"}},
    5: {"name": "Lizard", "beat": {2: "Lizard eats paper", 4: "Lizard poisons Spock"}}
}

game_items_easy = {
    1: {"name": "Scissors", "beat": {2: "Scissors cuts paper"}},
    3: {"name": "Rock", "beat": {1: "Rock crushes scissors"}},
    2: {"name": "Paper", "beat": {3: "Paper covers rock"}},
}


game_modes = {
    2: {"name": "normal", "game_items": game_items_normal},
    1: {"name": "easy", "game_items": game_items_easy},
}

def get_item(id: int, difficulty: int):
    return GameItemMeta(id, **game_modes[difficulty]["game_items"][id])

'''a = get_item(3)
b = get_item(4)

#r = GameResult().get_result(a, b)
#print(r)

for i in range(1, len(game_items)+1, 1):
    for j in range(len(game_items), 0, -1):
        print(GameResult(get_item(i), get_item(j)))'''