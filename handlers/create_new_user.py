import string
import secrets
import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta


from DB.connect_bd import insert_data_users_bd, check_user_name_users_bd, get_all_tariff, get_tariff
from gen_qrcode.generate_qr import generate_code
from mikrotik_control import mikro_hadlers


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
        await message.reply("Вносимая сумма руб. (цифрами)")


def generate_users_tarif(data):
    markup = InlineKeyboardMarkup(row_width=2)
    for i in data:
        markup.insert(InlineKeyboardButton(text=i, callback_data=i))
    return markup


async def process_user_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    if data['price'].isdigit() is not True:
        await message.reply('Введите суму цифрами, либо 0')
    else:
        await CreateNewUsers.next()
        await message.reply("Выберите тариф для пользователя", reply_markup=generate_users_tarif(get_all_tariff()))


async def process_payment_duration(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['tariff'] = callback.data
    await callback.answer("")
    kb = InlineKeyboardMarkup(row_width=2).insert(InlineKeyboardButton(text="Поддтвердить и сохранить",
                                                                    callback_data="save_new_user")) \
        .insert(InlineKeyboardButton(text="Отменить", callback_data="cancel_handler"))
    block = 'Внесенной суммы недостаточно для активации тарифа'
    not_block = f"Активация тарифа - {datetime.now().strftime('%d.%m.%Y')}"

    await callback.message.answer(
        md.text('Проверьте введенные данные!\n',
                md.text('Пользователь:', data['user_name']),
                md.text('Внесено руб:', data['price']),
                md.text('Тариф:', f"{data['tariff']} \n"
                                  f""
                                  f"{block if int(data['price']) < int(get_tariff(data['tariff'], type_search='price')) else not_block}"),
                sep='\n'
                ),
        reply_markup=kb,
    )
    await CreateNewUsers.next()


def generate_key():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(43))
    return f"{password}="


async def check_and_save(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.answer("")
        key = generate_key()

        if callback.data == "save_new_user":
            tariff_speed = get_tariff(data['tariff'], type_search='speed')
            tariff_price = get_tariff(data['tariff'], type_search='price')

            current_date = datetime.now()

            if int(data['price']) < int(tariff_price):
                next_date = current_date
                blocked = True
            else:
                data['price'] = int(data['price']) - int(tariff_price)
                next_date = current_date + timedelta(weeks=4)
                blocked = False

            ssh = mikro_hadlers.ControlMikrotik()
            ip = ssh.get_free_ip()
            ssh.create_new_users(ip, key, data['user_name'])
            ssh.create_queue_users(ip, data['user_name'])
            ssh.init_disconnect_mikro()

            insert_data_users_bd([data['user_name'], tariff_price, data['price'], key, next_date.strftime('%d.%m.%Y'),
                                  blocked, tariff_speed, current_date.strftime('%d.%m.%Y %H:%M')])

            generate_code(client_priv_key=generate_key(), current_ip=ip, server_pub_key=key)

            photo = open('code.png', 'rb')
            conf_file = open('conf_settings.txt', 'rb')
            await callback.message.answer_photo(photo, caption="config")
            await callback.message.answer_document(conf_file)

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
    bot.register_callback_query_handler(process_payment_duration, state=CreateNewUsers.payment_duration)
    bot.register_callback_query_handler(check_and_save, state=CreateNewUsers.check_and_save)
