import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv('.env')
token = os.getenv("TOKEN_API")

bot = Bot(token)
