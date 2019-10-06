import typing
import uuid
from random import randint

from loguru import logger

from models.item import GameItem, get_item
from models.user import User, FakeUser

import config


class GameSession:
    def __init__(self, first: User, second: typing.Union[FakeUser, User], difficulty: int, is_with_bot: bool = False):
        self.first: User = first
        self.second: typing.Union[FakeUser, User] = second
        self.game_with_bot: bool = is_with_bot
        self.difficulty: int = difficulty
        self.session_id: uuid.UUID = uuid.uuid4()
        self.winner: typing.Optional[User] = None
        self.defeated: typing.Optional[User] = None

    def set_user_choice(self, user: User, choice_id: int) -> None:
        logger.info(repr(choice_id))
        user.choice = get_item(choice_id, self.difficulty)
        if self.game_with_bot:
            self.second.choice = get_item(randint(1, len(config.game_modes[self.difficulty]["game_items"])) + 1, self.difficulty)

    def get_session_user(self, user_id: int) -> User:
        return self.first if self.first.id == user_id else self.second

    def is_all_user_maked_choice(self) -> bool:
        return True if (self.first.choice.id != -1 and self.second.choice.id != -1) else False

    def result(self) -> typing.List[typing.Union[User, None]]:
        self.winner = self.first if self.second.choice.id in self.first.choice.beat else (
            self.second if self.first.choice.id in self.second.choice.beat else None)
        self.defeated = None if self.winner is None else (self.first if self.first.choice.id in self.second.choice.beat else (
            self.second if self.second.choice.id in self.first.choice.beat else None))

        return [self.winner, self.defeated]

    def restart(self, user: User):
        self.winner = None
        self.defeated = None
        self.first.choice = GameItem(-1, 'def', {})
        self.second.choice = GameItem(-1, 'def', {})

    def __str__(self):
        return f"GameSession first {self.first} second {self.second} winner {self.winner} defeated {self.defeated}"
