import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.handlers.main_commands_handlers import registrate_main_commands
from bot.handlers.registration_handlers import registser_user_handlers
from bot.handlers.add_game_handlers import register_add_game_handlers
from bot.handlers.office_handlers import register_office_handlers
from bot.handlers.tournaments_handlers import register_tournaments_handlers
from bot.handlers.members_tournaments_handlers import register_members_tournament_handlers


def register_handlers(dp: Dispatcher) -> None:
    registrate_main_commands(dp=dp)
    registser_user_handlers(dp=dp)
    register_add_game_handlers(dp=dp)
    register_office_handlers(dp=dp)
    register_tournaments_handlers(dp=dp)
    register_members_tournament_handlers(dp=dp)


buffer = dict()


load_dotenv('.env')
token = os.getenv("TOKEN_API")
bot = Bot(token)


async def main() -> None:
    """
    Entry point
    """

    global bot

    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    register_handlers(dp=dp)

    try:
        await dp.start_polling()
    except Exception as _ex:
        print(f'There is an exception - {_ex}')


if __name__ == '__main__':
    asyncio.run(main())
