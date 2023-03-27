import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bots
from DB.connect_bd import insert_data_users_bd, check_user_name_users_bd


class CreateNewUsers(StatesGroup):
    user_name = State()
    price = State()
    payment_duration = State()
    check_and_save = State()


async def cmd_check(callback: types.CallbackQuery):
    await CreateNewUsers.user_name.set()
    await callback.answer("")
    await callback.message.answer("Введите имя пользователя")


async def process_user_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = message.text
    if check_user_name_users_bd(data['user_name']):
        await message.reply('Пользователь с таким логином уже существует, измените его название')
    else:
        await CreateNewUsers.next()
        await message.reply("Введите стоимость")


async def process_user_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

    await CreateNewUsers.next()
    await message.reply("Введите срок оплаты")


async def process_payment_duration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['payment_duration'] = message.text

    kb = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton(text="Поддтвердить и сохранить",
                                                                    callback_data="save_new_user")) \
        .add(InlineKeyboardButton(text="Отменить", callback_data="cancel_handler"))

    await bots.send_message(
        message.chat.id,
        md.text('Проверьте введенные данные!\n',
                md.text('Пользователь:', data['user_name']),
                md.text('Стоимость:', data['price']),
                md.text('Срок оплаты:', data['payment_duration']),
                sep='\n'
                ),
        reply_markup=kb,
        parse_mode=ParseMode.MARKDOWN,
    )
    await CreateNewUsers.next()


async def check_and_save(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data == "save_new_user":
            insert_data_users_bd([data['user_name'], data['price'], data['payment_duration']])
            await callback.message.answer("Новый пользователь успешно сохранен")
        else:
            await callback.message.answer("Отменено создание нового пользователя"),

        current_state = await state.get_state()
        if current_state is None:
            return

        await state.finish()


def register_handler_create_new_user(bot: Dispatcher):
    bot.register_callback_query_handler(cmd_check, text='create_new_user')
    bot.register_message_handler(process_user_name, state=CreateNewUsers.user_name)
    bot.register_message_handler(process_user_price, state=CreateNewUsers.price)
    bot.register_message_handler(process_payment_duration, state=CreateNewUsers.payment_duration)
    bot.register_callback_query_handler(check_and_save, state=CreateNewUsers.check_and_save)
