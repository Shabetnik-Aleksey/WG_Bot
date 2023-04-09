from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bots
from DB.connect_bd import get_all_users, value_update, get_pay_this_mouth
from mikrotik_control import mikro_hadlers


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
    Метод возвращает всех peer созданых в роутере
    :param callback:
    :return:
    """
    ssh = mikro_hadlers.ControlMikrotik()
    ssh.get_peers_all()
    ssh.init_disconnect_mikro()

    conf_file = open('all_users.txt', 'rb')
    await callback.answer("")
    await callback.message.answer_document(conf_file)


def generate_users_markup(data):
    """
    Генератор клавиатру
    :param data:
    :return:
    """
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    for i in data:
        markup.insert(InlineKeyboardButton(text=i, callback_data=i))
    markup.insert(InlineKeyboardButton(text="Отмена", callback_data="cancel_handler"))

    return markup


def generate_users_markup_dict(data):
    """
    Генератор клавиатру
    :param data:
    :return:
    """
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    for i in data:
        markup.add(InlineKeyboardButton(text=f"{i['name']} дата списания: {i['date']}, сумма в месяц - {i['price']}",
                                        callback_data=i['name']))
    return markup


async def blocking_and_deleting_users(callback: types.CallbackQuery):
    await UserManagement.user_name.set()
    await callback.answer("")
    await UserManagement.next()
    await callback.message.answer('Список пользователей:', reply_markup=generate_users_markup(get_all_users()))


async def blocking_and_deleting_users_step_2(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['user_name'] = callback.data

    kb = InlineKeyboardMarkup(row_width=2).insert(
        InlineKeyboardButton(text="Disable peer", callback_data="disable_peer")) \
        .insert(
        InlineKeyboardButton(text="Delete peer", callback_data="delete_peer")) \
        .insert(InlineKeyboardButton(text="Отмена", callback_data="canceled_manage_user")) \
        .insert(InlineKeyboardButton(text="Enable peer", callback_data="enable_manage_user"))
    await callback.answer("")
    await callback.message.answer(f'Пользователь: {callback.data}', reply_markup=kb)
    await UserManagement.next()


async def blocking_and_deleting_users_step_3(callback: types.CallbackQuery, state: FSMContext):

    async with state.proxy() as data:
        if callback.data == "disable_peer":

            ssh = mikro_hadlers.ControlMikrotik()
            ssh.change_state_peers(ssh.get_id_peers(data['user_name']), state_peer='disable_peer',
                                   user_name=data['user_name'])
            ssh.init_disconnect_mikro()

            value_update(data['user_name'], '1')
            await callback.answer("")
            await callback.message.answer(f"Успешно заблоикрован peer для {data['user_name']}")

        elif callback.data == "enable_manage_user":

            ssh = mikro_hadlers.ControlMikrotik()
            ssh.change_state_peers(ssh.get_id_peers(data['user_name']), state_peer='enable_manage_user',
                                   user_name=data['user_name'])
            ssh.init_disconnect_mikro()

            value_update(data['user_name'], '0')
            await callback.answer("")
            await callback.message.answer(f"Успешно активирован peer для {data['user_name']}")

        elif callback.data == "delete_peer":

            ssh = mikro_hadlers.ControlMikrotik()
            ssh.change_state_peers(ssh.get_id_peers(data['user_name']), state_peer='delete_peer',
                                   user_name=data['user_name'])
            ssh.init_disconnect_mikro()

            value_update(data['user_name'], '2', typs='delete_row')
            await callback.answer("")
            await callback.message.answer(f"Успешно удален peer для {data['user_name']}")

        else:
            await callback.answer("")
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

        ssh = mikro_hadlers.ControlMikrotik()
        ssh.create_queue_users(data['user_name'], data['user_speed'], type_set='set')
        ssh.init_disconnect_mikro()

        value_update(data['user_name'], data['user_speed'], 'speed')
        await bots.send_message(message.chat.id, f"Выставили ограничение скорости в {message.text}")
        await state.finish()
    else:
        await bots.send_message(message.chat.id, f"Введите цифры")


async def payments_users_in_this_mounts(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2) \
        .insert(InlineKeyboardButton(text="платить в этом месяце", callback_data="show_pay_users")) \
        .insert(InlineKeyboardButton(text="Внести оплату", callback_data="make_a_payment")) \
        .insert(InlineKeyboardButton(text="Управление тарифами", callback_data="tariff_management_wg")) \

    await callback.answer("")
    await callback.message.answer("Меню управления оплатами", reply_markup=kb)


async def make_a_payment_users_step_1(callback: types.CallbackQuery):
    await UserManagementMakePayment.user_name.set()
    await callback.answer("")
    await UserManagementMakePayment.next()
    await callback.message.answer("Выбор пользователя для внесения оплаты",
                                  reply_markup=generate_users_markup(get_all_users()))


async def payments_users_in_this_mounts_step_2(callback: types.CallbackQuery):

    if get_pay_this_mouth():
        await UserManagementMakePayment.user_name.set()
        await callback.answer("")
        await UserManagementMakePayment.next()
        await callback.message.answer("Этим пользователям необходимо оплатить в этом месяце",
                                      reply_markup=generate_users_markup_dict(get_pay_this_mouth()))
    else:
        await callback.message.answer('Нет пользователей, которым необходимо вносить оплату в этом месяце')


async def make_payments_users_step_2(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    async with state.proxy() as data:
        data['user_name'] = callback.data
    if data['user_name'] == 'cancel_handler':
        await state.finish()
        await callback.message.answer('Действие отменено')
    else:
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
    # make_a_payment
    bot.register_callback_query_handler(make_a_payment_users_step_1, text='make_a_payment')
