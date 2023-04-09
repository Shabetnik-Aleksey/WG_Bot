from aiogram import types
from aiogram import Dispatcher

from mikrotik_control import mikro_hadlers


async def cmd_check(callback: types.CallbackQuery):
    ssh = mikro_hadlers.ControlMikrotik()
    ss = ssh.get_system_resource()
    ssh.init_disconnect_mikro()
    await callback.answer("")
    await callback.message.answer(ss)


def register_handler_resource_status(bot: Dispatcher):
    bot.register_callback_query_handler(cmd_check, text='resource_status')
