import sqlite3

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
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def create_new_table_users_tariff():
    try:
        sqlite_connection = sqlite3.connect(PATH_BD)
        sqlite_create_table_query = '''CREATE TABLE wg_tariff (
                                    id INTEGER PRIMARY KEY,
                                    title_tarif TEXT NOT NULL UNIQUE,
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
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")




def insert_data_users_bd(value):
    conn = sqlite3.connect(PATH_BD)
    cur = conn.cursor()
    cur.execute("INSERT INTO 'wg_users' (name, price, balance, key, date_pay, blocked, speed, joining_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", value)
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
    cur.execute(f"select title_tarif from wg_tariff")
    title_tariff = cur.fetchall()
    return title_tariff


def get_tariff(value, type_search='speed'):
    conn = sqlite3.connect(PATH_BD)
    conn.row_factory = lambda cursor, row: row[0]
    cur = conn.cursor()
    if type_search == 'speed':
        cur.execute(f"select speed from 'wg_tariff' where `title_tarif` = '{value}'")
    elif type_search == 'price':
        cur.execute(f"select price from 'wg_tariff' where `title_tarif` = '{value}'")
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
    if typs == 'balance':
        cur.execute(f'''UPDATE 'wg_users' SET {typs} = ? WHERE name = ?''', (value, name))
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
    cur.execute(f"SELECT name, price, balance, blocked, date_pay, (balance / price) FROM wg_users WHERE(balance / price) <= 0")
    title_tariff = cur.fetchall()
    return title_tariff


if __name__ == '__main__':
    # insert_data_users_bd(['misha3324', '112', '12.02.2222'])
    # value_update()
    get_pay_this_mouth()
