import datetime
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from create_bot import telegram_bot_sendtext

PATH_BD = 'wg_bot.db'


def create_new_table_users():
    try:
        sqlite_connection = sqlite3.connect(PATH_BD)
        sqlite_create_table_query = '''CREATE TABLE wg_users (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT NOT NULL UNIQUE,
                                    price INTEGER NOT NULL,
                                    balance INTEGER DEFAULT 0,
                                    key TEXT NOT NULL,
                                    date_pay datetime,
                                    blocked BOOL DEFAULT false,
                                    speed INTEGER DEFAULT 10,
                                    joining_date datetime);'''

        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")
        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()
        print("Таблица SQLite создана")

        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)


def create_new_table_users_tariff():
    try:
        sqlite_connection = sqlite3.connect(PATH_BD)
        sqlite_create_table_query = '''CREATE TABLE wg_tariff (
                                    id INTEGER PRIMARY KEY,
                                    title_tariff TEXT NOT NULL UNIQUE,
                                    speed INTEGER,
                                    price INTEGER);'''

        cursor = sqlite_connection.cursor()
        print("База данных подключена к SQLite")
        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()
        print("Таблица SQLite создана")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)


def insert_data_users_bd(value, table='wg_users'):
    conn = sqlite3.connect(PATH_BD)
    cur = conn.cursor()
    if table == 'wg_users':
        cur.execute("INSERT INTO 'wg_users' (name, price, balance, key, date_pay, blocked, speed, joining_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", value)
    if table == 'wg_tariff':
        cur.execute("INSERT INTO 'wg_tariff' (title_tariff, speed, price) VALUES (?, ?, ?)", value)
    conn.commit()


def check_user_name_users_bd(value):
    conn = sqlite3.connect(PATH_BD)
    cur = conn.cursor()
    cur.execute(f"select name from 'wg_users' where `name` = '{value}'")
    name = cur.fetchone()
    return True if name else False


def get_all_tariff():
    conn = sqlite3.connect(PATH_BD)
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    cur.execute(f"select title_tariff from wg_tariff")
    title_tariff = cur.fetchall()
    return title_tariff


def get_tariff(value, type_search='speed'):
    conn = sqlite3.connect(PATH_BD)
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    if type_search == 'speed':
        cur.execute(f"select speed from 'wg_tariff' where `title_tariff` = '{value}'")
    elif type_search == 'price':
        cur.execute(f"select price from 'wg_tariff' where `title_tariff` = '{value}'")
    name = cur.fetchone()
    return name


def get_users(value, type_search='users'):
    conn = sqlite3.connect(PATH_BD)
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    if type_search == 'users':
        cur.execute(f"select name from 'wg_users' where `name` = '{value}'")
    elif type_search == 'price':
        cur.execute(f"select price from 'wg_users' where `title_tarif` = '{value}'")
    name = cur.fetchone()
    return name


def value_update(name, value, typs='blocked'):
    conn = sqlite3.connect(PATH_BD)
    cur = conn.cursor()
    if typs == 'blocked':
        cur.execute(f'''UPDATE 'wg_users' SET {typs} = ? WHERE name = ?''', (value, name))

    elif typs == 'balance':
        cur.execute(f"select name from 'wg_users' where `name` = '{name}' AND blocked == 1")
        blocked = cur.fetchall()
        cur.execute(f"select balance from 'wg_users' where `name` = '{name}'")
        remainder = cur.fetchone()
        next_date = datetime.now() + timedelta(weeks=4)
        new_balance = int(value) + int(remainder[0])
        cur.execute(f'''UPDATE 'wg_users' SET balance = ? WHERE name = ?''', (new_balance, name))
        cur.execute(f'''UPDATE 'wg_users' SET blocked = 0 WHERE name = ?''', (name,))
        if blocked:
            cur.execute(f'''UPDATE 'wg_users' SET date_pay = ? WHERE name = ?''', (next_date.strftime('%d.%m.%Y'), name))

    elif typs == 'speed':
        cur.execute(f'''UPDATE 'wg_users' SET {typs} = ? WHERE name = ?''', (value, name))

    elif typs == 'delete_row':
        cur.execute(f'''DELETE from 'wg_users' WHERE name = ?''', (name, ))
    conn.commit()


def value_delete(name, tables='wg_users'):
    conn = sqlite3.connect(PATH_BD)
    cur = conn.cursor()

    if tables == 'wg_users':
        cur.execute(f'''DELETE from 'wg_users' WHERE name = ?''', (name,))

    elif tables == 'wg_tariff':
        cur.execute(f'''DELETE from 'wg_tariff' WHERE title_tariff = ?''', (name,))

    conn.commit()


def get_all_users():
    conn = sqlite3.connect(PATH_BD)
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    cur.execute(f"select name from wg_users")
    title_tariff = cur.fetchall()
    return title_tariff


def get_pay_this_mouth():
    conn = sqlite3.connect(PATH_BD)
    conn.row_factory = lambda cursor, row: {'name': row[0], 'date': row[4], 'price': row[1]}
    cur = conn.cursor()
    cur.execute(
        f"SELECT name, price, balance, blocked, date_pay FROM wg_users WHERE(balance / price) <= 0")
    title_tariff = cur.fetchall()
    return title_tariff


def spisanie():
    base_dir = Path(__file__).resolve().parent.parent
    conn = sqlite3.connect(f'{base_dir}/wg_bot.db')
    conn.row_factory = lambda cursor, row: {'name': row[0], 'date': row[4], 'price': row[1], "balance": row[2]}
    cur = conn.cursor()
    data = datetime.now().strftime('%d.%m.%Y')
    cur.execute(
        f"SELECT name, price, balance, blocked, date_pay FROM wg_users WHERE date_pay == ? AND blocked == 0 and (balance / price) > 0", (data,))
    title_tariff = cur.fetchall()

    for i in title_tariff:
        telegram_bot_sendtext(f"Списали у пользователя {i['name']} - {i['price']}руб, в остатке {i['balance'] - i['price']}")

        new_balance = i['balance'] - i['price']
        next_date = datetime.now() + timedelta(weeks=4)
        cur.execute(f'''UPDATE 'wg_users' SET balance = ?, date_pay = ? WHERE name = ?''', (new_balance, next_date.strftime('%d.%m.%Y'), i['name']))

    conn.commit()

    cur.execute(
        f"SELECT name, price, balance, blocked, date_pay FROM wg_users WHERE date_pay == ? AND blocked == 0 and (balance / price) <= 0",
        (data,))
    title_tariff = cur.fetchall()
    for i in title_tariff:
        telegram_bot_sendtext(f"Заблокировали {i['name']}, на счету не хватает денег для оплаты необходимо внести {i['balance'] - i['price']}")

        value_update(i['name'], value=1, typs='blocked')
    return title_tariff


if __name__ == '__main__':
    spisanie()
