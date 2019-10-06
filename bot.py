import logging
import random
import typing
import uuid
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, md, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled
from loguru import logger

from item import GameItemMeta, GameResult, game_modes, get_item
import config
from random import choice

logging.basicConfig(level=logging.INFO)

API_TOKEN = '633835687:AAGx4ZNz3GzEpZi3mjdmLYZPLcAojWA_VR0'


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


menu_cb = CallbackData('menu', 'action', 'difficulty')  # menu:<action>
item_cb = CallbackData('game', 'action', 'session_id', 'item_id', 'difficulty')


class User:
    def __init__(self, id: int, msg_id: int, diff: int):
        self.id: int = id
        self.message_id: int = msg_id
        self.difficulty: int = diff
        self.start_wait_at: datetime = datetime.now()
        self.choice: GameItemMeta = GameItemMeta(-1, 'def', {})

    def __str__(self) -> str:
        return f"User {self.id} msg {self.message_id} choice {self.choice} diff {self.difficulty}"

    def __repr__(self):
        return str(self)


class GameSession:
    def __init__(self, first: User, second: User, difficulty: int):
        self.first: User = first
        self.second: User = second
        self.difficulty: int = difficulty
        self.session_id: uuid.UUID = uuid.uuid4()
        self.winner: typing.Optional[User] = None
        self.defeated: typing.Optional[User] = None

    def set_user_choice(self, user: User, choice_id: int) -> None:
        logger.info(repr(choice_id))
        user.choice = get_item(choice_id, self.difficulty)

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
        self.first.choice = GameItemMeta(-1, 'def', {})
        self.second.choice = GameItemMeta(-1, 'def', {})

    def __str__(self):
        return f"GameSession first {self.first} second {self.second} winner {self.winner} defeated {self.defeated}"


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


user_games_pool: UserGamesPool = UserGamesPool()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(
        'Start game Easy',
        callback_data=menu_cb.new(action='start_game', difficulty = '1')),
        types.InlineKeyboardButton(
        'Start game Normal',
        callback_data=menu_cb.new(action='start_game', difficulty = '2')))

    await message.answer('Click but', reply_markup=markup)


@dp.callback_query_handler(menu_cb.filter(action='start_game'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    diff: int = int(callback_data['difficulty'])
    user: User = User(query.from_user.id, query.message.message_id, diff)
    user_games_pool.add_user(user)
    opponent: typing.Optional[User] = user_games_pool.find_user(user)
    logger.info(opponent)
    if not opponent:
        await query.message.edit_text('wait, i searching peple for you...')
    else:
        
        gs: GameSession = user_games_pool.create_game_session(user, opponent, diff)
        items_kb = types.InlineKeyboardMarkup().add(
            *[types.InlineKeyboardButton(
                item["name"],
                callback_data=item_cb.new(action='choice', session_id=gs.session_id, item_id=key_id, difficulty=diff)) for key_id, item in game_modes[diff]['game_items'].items()]
        )
        await query.message.edit_text(f'You can start game i found opponent for you!\nPlease choose one from this buttons', reply_markup=items_kb)
        await bot.edit_message_text(f'You can start game i found opponent for you!\nPlease choose one from this buttons', opponent.id, opponent.message_id, reply_markup=items_kb)


@dp.callback_query_handler(item_cb.filter(action='choice'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    logger.info(user_games_pool.game_sessions)
    logger.info(callback_data["session_id"])
    gs: typing.Optional[GameSession] = user_games_pool.get_session(
        callback_data["session_id"])
    logger.info(gs)
    gs.set_user_choice(gs.get_session_user(
        query.from_user.id), int(callback_data['item_id']))
    ch: bool = gs.is_all_user_maked_choice()
    logger.info(ch)
    logger.info(gs)
    if ch:
        res = gs.result()
        logger.info(res)
        replay_kb = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton(
                "Play again",
                callback_data=menu_cb.new(action='start_game', difficulty=callback_data['difficulty']))
        )
        if any(res):
            await bot.edit_message_text(f"You won!\nYou choose <pre>{gs.winner.choice.name}</pre>\nOpponent choose <pre>{gs.defeated.choice.name}</pre>\n<b>{gs.winner.choice.description[gs.defeated.choice.id]}</b>", gs.winner.id, gs.winner.message_id, reply_markup=replay_kb)
            await bot.edit_message_text(f"You lose :(\nYou choose <pre>{gs.defeated.choice.name}</pre>\nOpponent choose <pre>{gs.winner.choice.name}</pre>\n<b>{gs.winner.choice.description[gs.defeated.choice.id]}</b>", gs.defeated.id, gs.defeated.message_id, reply_markup=replay_kb)
        else:
            await bot.edit_message_text(f"It`s draw\nYou choose <pre>{gs.first.choice.name}</pre>\nOpponent choose <pre>{gs.second.choice.name}</pre>", gs.first.id, gs.first.message_id, reply_markup=replay_kb)
            await bot.edit_message_text(f"It`s draw\nYou choose <pre>{gs.second.choice.name}</pre>\nOpponent choose <pre>{gs.first.choice.name}</pre>", gs.second.id, gs.second.message_id, reply_markup=replay_kb)

        user_games_pool.delete_session(callback_data["session_id"])
    else:
        await query.message.edit_text("Waiting for you opponent")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
