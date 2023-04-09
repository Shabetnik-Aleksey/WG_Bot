from aiogram import Bot, Dispatcher
import settings
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests


def telegram_bot_sendtext(bot_message):
    bot_token = settings.TEL_KEY
    bot_chat_id = settings.BOT_CHAT_ID
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?' \
                f'chat_id={bot_chat_id}&parse_mode=Markdown&text={bot_message}'

    response = requests.get(send_text)

    return response.json()


logging.basicConfig(level=logging.INFO)


bots = Bot(token=settings.TEL_KEY)

storage = MemoryStorage()
bot = Dispatcher(bots, storage=storage)
