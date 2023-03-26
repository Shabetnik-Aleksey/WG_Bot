from aiogram import types
from aiogram import Dispatcher


async def cmd_check(callback: types.CallbackQuery):
    await callback.answer("")
    await callback.message.answer("Состояние ресурсов")


def register_handler_resource_status(bot: Dispatcher):
    bot.register_callback_query_handler(cmd_check, text='resource_status')
