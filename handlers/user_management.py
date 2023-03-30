from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bots
from DB.connect_bd import get_all_users, value_update, get_pay_this_mouth


class UserManagement(StatesGroup):

    user_name = State()
    change_user_step_2 = State()
    change_user_step_3 = State()


class UserManagementRestrictions(StatesGroup):

    user_name = State()
    set_user_speed = State()


class UserManagementMakePayment(StatesGroup):

    user_name = State()
    set_user_payment = State()
    set_user_payment2 = State()


async def process_payment_duration(callback: types.CallbackQuery):

    kb = InlineKeyboardMarkup(row_width=2)
    urlbutton = InlineKeyboardButton(text="Показать пользователей", callback_data="show_all_users")
    urlbutton2 = InlineKeyboardButton(text="Блокировка и удаление", callback_data="blocking_and_del_users")
    urlbutton3 = InlineKeyboardButton(text="Ограничения", callback_data="restrictions")
    urlbutton4 = InlineKeyboardButton(text="Оплаты", callback_data="payments_users")
    kb.add(urlbutton, urlbutton2, urlbutton3, urlbutton4)

    await callback.answer("")
    await callback.message.answer("Меню управления пользователями", reply_markup=kb)


async def show_all_users(callback: types.CallbackQuery):
    """
    Метод возвращает всех абонентов в базе данных
    :param callback:
    :return:
    """

    await callback.answer("")
    await callback.message.answer("Показать всех абонентов")


def generate_users_markup(data):

    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    for i in data:
        markup.add(InlineKeyboardButton(text=i, callback_data=i))
    return markup


def generate_users_markup_dict(data):

    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    for i in data:
        markup.add(InlineKeyboardButton(text=f"{i['name']} дата списания: {i['date']}, сумма в месяц - {i['price']}", callback_data=i['name']))
    return markup


async def blocking_and_deleting_users(callback: types.CallbackQuery):
    await UserManagement.user_name.set()
    await callback.answer("")
    await UserManagement.next()
    await callback.message.answer('Список пользователей:', reply_markup=generate_users_markup(get_all_users()))


async def blocking_and_deleting_users_step_2(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = callback.data

    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text="Disable peer", callback_data="disable_peer")) \
        .add(
        InlineKeyboardButton(text="Delete peer", callback_data="delete_peer")) \
        .add(InlineKeyboardButton(text="Отмена", callback_data="canceled_manage_user"))
    await callback.answer("")
    await callback.message.answer(f'Пользователь: {callback.data}', reply_markup=kb)
    await UserManagement.next()


async def blocking_and_deleting_users_step_3(callback: types.CallbackQuery, state: FSMContext):

    async with state.proxy() as data:
        if callback.data == "disable_peer":
            value_update(data['user_name'], '1')
            await callback.message.answer(f"Успешно заблоикрован peer для {data['user_name']}")

        elif callback.data == "delete_peer":
            value_update(data['user_name'], '2')
            await callback.message.answer(f"Успешно удален peer для {data['user_name']}")

        else:
            await callback.message.answer(f"Отмена для {data['user_name']}")

        await state.finish()


async def get_all_restrictions_users(callback: types.CallbackQuery):
    await UserManagement.user_name.set()
    await callback.answer("")
    await UserManagementRestrictions.next()
    await callback.message.answer('Список пользователей:', reply_markup=generate_users_markup(get_all_users()))


async def restrictions_users(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = callback.data
    await callback.answer("")
    await UserManagementRestrictions.next()
    await callback.message.answer('Введите скорость в Мб/с')


async def restrictions_users_speed(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_speed'] = message.text

    if message.text.isdigit():
        value_update(data['user_name'], data['user_speed'], 'speed')
        await bots.send_message(message.chat.id, f"Выставили ограничение скорости в {message.text}")
        await state.finish()
    else:
        await bots.send_message(message.chat.id, f"Введите цифры")


async def payments_users_in_this_mounts(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2) \
        .add(InlineKeyboardButton(text="Показать пользователей, которым платить в этом месяце",
                                  callback_data="show_pay_users")) \
        .add(InlineKeyboardButton(text="Показать дату следующей блокировки", callback_data="next_lock_date")) \

    await callback.message.answer("Меню управления оплатами", reply_markup=kb)


async def payments_users_in_this_mounts_step_2(callback: types.CallbackQuery):
    await UserManagementMakePayment.user_name.set()
    await callback.answer("")
    await UserManagementMakePayment.next()
    await callback.message.answer("Этим пользователям необходимо оплатить в этом месяце"
                                  , reply_markup=generate_users_markup_dict(get_pay_this_mouth()))


async def make_payments_users_step_2(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = callback.data
    await UserManagementMakePayment.next()
    await callback.message.answer('Введите сумму пополнения')


async def make_payments_users_step_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_pay'] = message.text

    if message.text.isdigit():
        value_update(data['user_name'], data['user_pay'], typs='balance')
        await state.finish()
        await bots.send_message(message.chat.id, f"Оплата пользователю {data['user_name']} успешно внесена")
    else:
        await bots.send_message(message.chat.id, f"Введите цифры")


def register_handler_user_management(bot: Dispatcher):
    bot.register_callback_query_handler(process_payment_duration, text='user_management')
    # show_all_users
    bot.register_callback_query_handler(show_all_users, text='show_all_users')
    # blocking_and_deleting
    bot.register_callback_query_handler(blocking_and_deleting_users, text='blocking_and_del_users')
    bot.register_callback_query_handler(blocking_and_deleting_users_step_2, state=UserManagement.change_user_step_2)
    bot.register_callback_query_handler(blocking_and_deleting_users_step_3, state=UserManagement.change_user_step_3)
    # restrictions get_all_restrictions_users
    bot.register_callback_query_handler(get_all_restrictions_users, text='restrictions')
    bot.register_callback_query_handler(restrictions_users, state=UserManagementRestrictions.user_name)
    bot.register_message_handler(restrictions_users_speed, state=UserManagementRestrictions.set_user_speed)
    # payments
    bot.register_callback_query_handler(payments_users_in_this_mounts, text='payments_users')
    bot.register_callback_query_handler(payments_users_in_this_mounts_step_2, text='show_pay_users')
    bot.register_callback_query_handler(make_payments_users_step_2, state=UserManagementMakePayment.set_user_payment)
    bot.register_message_handler(make_payments_users_step_3, state=UserManagementMakePayment.set_user_payment2)
