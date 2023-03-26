from aiogram import Bot, Dispatcher
import settings
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)


bots = Bot(token=settings.TEL_KEY)

storage = MemoryStorage()
bot = Dispatcher(bots, storage=storage)
