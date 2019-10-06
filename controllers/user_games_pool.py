import typing
import uuid
from datetime import datetime, timedelta

from loguru import logger

import config
from controllers.game_session import GameSession
from models.user import User


class UserGamesPool:
    def __init__(self):
        self.users_wait: typing.Dict[typing.Tuple[int, int], User] = {}
        self.game_sessions: typing.Dict[uuid.UUID, GameSession] = {}

    def add_user(self, user: User) -> None:
        self.users_wait[(user.message_id, user.id)] = user

    def find_user(self, for_user: User) -> typing.Union[None, User]:
        logger.info(len(self.users_wait))
        for user in self.users_wait.values():
            logger.info(datetime.now() - user.start_wait_at)
            if datetime.now() - user.start_wait_at < timedelta(minutes=config.SESSION_TIMEOUT):
                if user.id != for_user.id and user.difficulty == for_user.difficulty:
                    return user

        return None

    def create_game_session(self, first: User, second: User, difficulty: int) -> GameSession:
        del self.users_wait[(first.message_id, first.id)]
        del self.users_wait[(second.message_id, second.id)]

        gs = GameSession(first, second, difficulty)

        self.game_sessions[gs.session_id] = gs

        return gs

    def get_session(self, session_id: str) -> typing.Optional[GameSession]:
        return self.game_sessions.get(uuid.UUID(session_id))

    def delete_session(self, session_id: str) -> None:
        del self.game_sessions[uuid.UUID(session_id)]
