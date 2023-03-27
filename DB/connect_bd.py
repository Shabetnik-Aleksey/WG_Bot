import sqlite3

PATH_BD = 'wg_bot.db'


# def create_new_table_users():
#     try:
#         sqlite_connection = sqlite3.connect('wg_bot.db')
#         sqlite_create_table_query = '''CREATE TABLE wg_users (
#                                     id INTEGER PRIMARY KEY,
#                                     name TEXT NOT NULL UNIQUE,
#                                     price INTEGER NOT NULL,
#                                     date_pay datetime
#                                     joining_date datetime);'''
#
#         cursor = sqlite_connection.cursor()
#         print("База данных подключена к SQLite")
#         cursor.execute(sqlite_create_table_query)
#         sqlite_connection.commit()
#         print("Таблица SQLite создана")
#
#         cursor.close()
#
#     except sqlite3.Error as error:
#         print("Ошибка при подключении к sqlite", error)
#     finally:
#         if (sqlite_connection):
#             sqlite_connection.close()
#             print("Соединение с SQLite закрыто")


def insert_data_users_bd(value):
    conn = sqlite3.connect('wg_bot.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO 'wg_users' (name, price, date_pay) VALUES (?, ?, ?)", value)
    conn.commit()


def check_user_name_users_bd(value):
    conn = sqlite3.connect(PATH_BD)
    cur = conn.cursor()
    cur.execute(f"select name from wg_users where `name` = '{value}'")
    name = cur.fetchone()
    return True if name else False


if __name__ == '__main__':
    insert_data_users_bd(['misha3324', '112', '12.02.2222'])
