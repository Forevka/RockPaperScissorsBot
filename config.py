SESSION_TIMEOUT = 5 #minutes

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