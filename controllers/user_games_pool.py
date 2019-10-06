import typing
import uuid
from datetime import datetime, timedelta

from loguru import logger

import config
from controllers.game_session import GameSession
from models.user import User, FakeUser


class UserGamesPool:
    def __init__(self):
        self.users_wait: typing.Dict[typing.Tuple[int, int], User] = {}
        self.game_sessions: typing.Dict[uuid.UUID, GameSession] = {}

    def add_user(self, user: User) -> None:
        self.users_wait[(user.message_id, user.id)] = user
    
    def delete_user(self, user: typing.Union[FakeUser, User]) -> None:
        del self.users_wait[(user.message_id, user.id)]

    def get_stored_user(self, user_message_id: int, user_id: int) -> User:
        return self.users_wait[(user_message_id, user_id)]

    def find_bot(self, for_user: User) -> FakeUser:
        return FakeUser(-1, -1, for_user.difficulty)

    def find_user(self, for_user: User) -> typing.Union[None, User]:
        logger.info(len(self.users_wait))
        
        for user in self.users_wait.values():
            logger.info(datetime.now() - user.start_wait_at)
            if datetime.now() - user.start_wait_at < timedelta(minutes=config.SESSION_TIMEOUT):
                if user.id != for_user.id and user.difficulty == for_user.difficulty:
                    return user
        
        return None

    def create_game_session(self, first: User, second: typing.Union[User, FakeUser], difficulty: int, is_with_bot: bool) -> GameSession:
        self.delete_user(first)
        if not is_with_bot:
            self.delete_user(second)

        gs = GameSession(first, second, difficulty, is_with_bot)

        self.game_sessions[gs.session_id] = gs

        return gs

    def get_session(self, session_id: str) -> typing.Optional[GameSession]:
        return self.game_sessions.get(uuid.UUID(session_id))

    def delete_session(self, session_id: str) -> None:
        del self.game_sessions[uuid.UUID(session_id)]
