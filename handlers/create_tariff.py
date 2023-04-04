from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from DB.connect_bd import insert_data_users_bd, get_all_tariff, value_delete


class CreateNewTariff(StatesGroup):
    tariff_name = State()
    tariff_speed = State()
    tariff_price = State()


class DeleteTariff(StatesGroup):
    tariff_name_delete = State()
    tariff_name_delete1 = State()
    tariff_name_delete2 = State()


async def tariff_management_settings(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2) \
        .insert(InlineKeyboardButton(text="Показать все тарифы", callback_data="show_tariff_users_wg")) \
        .insert(InlineKeyboardButton(text="Создать новый тариф", callback_data="create_new_tariff_wg")) \

    await callback.message.answer("Меню управления тарифами", reply_markup=kb)


def generate_users_tarif(data):
    markup = InlineKeyboardMarkup(row_width=2)
    for i in data:
        markup.insert(InlineKeyboardButton(text=i, callback_data=i))
    return markup


async def show_all_tariff(callback: types.CallbackQuery):
    await DeleteTariff.tariff_name_delete.set()
    await callback.answer("")
    await DeleteTariff.next()
    await callback.message.reply("Выберите тариф", reply_markup=generate_users_tarif(get_all_tariff()))


async def delete_wg_tariff_step_1(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['tariff_name'] = callback.data

    kb = InlineKeyboardMarkup(row_width=2) \
        .insert(InlineKeyboardButton(text="Удалить тариф", callback_data="delete_tariff_users_wg")) \
        .insert(InlineKeyboardButton(text="Отмена действий", callback_data="canceled_tariff_users_wg")) \

    await callback.answer("")
    await callback.message.answer(f"Действия для тарифа {data['tariff_name']}", reply_markup=kb)
    await DeleteTariff.next()


async def delete_wg_tariff_step_2(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['tariff_action'] = callback.data
    await callback.answer("")

    if data['tariff_action'] == "delete_tariff_users_wg":
        value_delete(data['tariff_name'], tables='wg_tariff')
        await state.finish()
        await callback.message.answer(f"Тариф {data['tariff_name']} успешно удален")
    else:
        await state.finish()
        await callback.message.answer(f"Отмена действий с тарифами")


async def create_new_tariff(callback: types.CallbackQuery):
    await CreateNewTariff.tariff_name.set()
    await callback.answer("")
    await callback.message.answer("Введите название нового тарифа")


async def process_tariff_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tariff_name'] = message.text
        await message.reply('Введите скорость тарифа')
        await CreateNewTariff.next()


async def process_tariff_speed(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tariff_speed'] = message.text
        if data['tariff_speed'].isdigit() is not True:
            await message.reply('Введите скорость тарифа цифрами')
        else:
            await CreateNewTariff.next()
            await message.reply('Введите стомость тарифа цифрами')


async def process_tariff_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tariff_price'] = message.text
        if data['tariff_price'].isdigit() is not True:
            await message.reply('Введите стомость тарифа цифрами')
        else:
            insert_data_users_bd([data['tariff_name'], data['tariff_speed'], data['tariff_price']], table='wg_tariff')
            await message.reply('Тариф успешно создан')
            await CreateNewTariff.next()


def register_handler_tariff(bot: Dispatcher):
    bot.register_callback_query_handler(tariff_management_settings, text='tariff_management_wg')
    bot.register_callback_query_handler(show_all_tariff, text='show_tariff_users_wg')
    # delete tariff
    bot.register_callback_query_handler(delete_wg_tariff_step_1, state=DeleteTariff.tariff_name_delete1)
    bot.register_callback_query_handler(delete_wg_tariff_step_2, state=DeleteTariff.tariff_name_delete2)
    # create new tariff
    bot.register_callback_query_handler(create_new_tariff, text='create_new_tariff_wg')
    bot.register_message_handler(process_tariff_name, state=CreateNewTariff.tariff_name)
    bot.register_message_handler(process_tariff_speed, state=CreateNewTariff.tariff_speed)
    bot.register_message_handler(process_tariff_price, state=CreateNewTariff.tariff_price)
