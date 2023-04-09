from aiogram.utils import executor
from create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram import types

from handlers import create_new_user, resource_status, user_management, create_tariff


@bot.message_handler(commands=['start'])
async def start_message(message):
    kb = InlineKeyboardMarkup(row_width=2)\
        .insert(InlineKeyboardButton(text="Управление пользователями", callback_data="user_management")) \
        .insert(InlineKeyboardButton(text="Новый пользователь", callback_data="create_new_user")) \
        .insert(InlineKeyboardButton(text="Состояние ресурсов", callback_data="resource_status"))
    await message.reply("Выбор необходимого действия", reply_markup=kb)


@bot.message_handler(state='*', commands='cancel')
async def cancel_handler(message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Выполненена отмена состояния.', reply_markup=types.ReplyKeyboardRemove())


create_new_user.register_handler_create_new_user(bot)
resource_status.register_handler_resource_status(bot)
user_management.register_handler_user_management(bot)
create_tariff.register_handler_tariff(bot)

if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=True)
