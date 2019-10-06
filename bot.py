import logging
import typing

from aiogram import Bot, Dispatcher, executor, md, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified, Throttled
from loguru import logger

import config
from controllers.game_session import GameSession
from models.item import game_modes
from models.user import User
from controllers.user_games_pool import UserGamesPool

logging.basicConfig(level=logging.INFO)

API_TOKEN = '633835687:AAGx4ZNz3GzEpZi3mjdmLYZPLcAojWA_VR0'


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


menu_cb = CallbackData('menu', 'action', 'difficulty')  # menu:<action>
item_cb = CallbackData('game', 'action', 'session_id', 'item_id', 'difficulty')

user_games_pool: UserGamesPool = UserGamesPool()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(
        'Start game Easy',
        callback_data=menu_cb.new(action='start_game', difficulty='1')),
        types.InlineKeyboardButton(
        'Start game Normal',
        callback_data=menu_cb.new(action='start_game', difficulty='2')))

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

        gs: GameSession = user_games_pool.create_game_session(
            user, opponent, diff)
        items_kb = types.InlineKeyboardMarkup().add(
            *[types.InlineKeyboardButton(
                item["name"],
                callback_data=item_cb.new(action='choice', session_id=gs.session_id, item_id=key_id, difficulty=diff)) for key_id, item in game_modes[diff]['game_items'].items()]
        )
        await query.message.edit_text(f'You can start game i found opponent for you!\nPlease choose one from this buttons', reply_markup=items_kb)
        await bot.edit_message_text(f'You can start game i found opponent for you!\nPlease choose one from this buttons', opponent.id, opponent.message_id, reply_markup=items_kb)


@dp.callback_query_handler(menu_cb.filter(action='start_game_bot'))
async def query_show_list(query: types.CallbackQuery, callback_data: dict):
    pass

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
        play_with_bot_kb = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton(
                "Play with bot",
                callback_data=menu_cb.new(action='start_game_bot', difficulty=callback_data['difficulty']))
        )
        await query.message.edit_text("Waiting for you opponent\nIf you dont want wait play with bot", reply_markup=play_with_bot_kb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
