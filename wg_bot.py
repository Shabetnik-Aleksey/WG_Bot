from aiogram.utils import executor
from create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers import create_new_user, resource_status, user_management, create_tariff


@bot.message_handler(commands=['start'])
async def start_message(message):
    kb = InlineKeyboardMarkup(row_width=2)\
        .insert(InlineKeyboardButton(text="Управление пользователями", callback_data="user_management")) \
        .insert(InlineKeyboardButton(text="Новый пользователь", callback_data="create_new_user")) \
        .insert(InlineKeyboardButton(text="Состояние ресурсов", callback_data="resource_status"))
    await message.reply("Выбор необходимого действия", reply_markup=kb)


create_new_user.register_handler_create_new_user(bot)
resource_status.register_handler_resource_status(bot)
user_management.register_handler_user_management(bot)
create_tariff.register_handler_tariff(bot)

if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=True)
