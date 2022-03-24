import telebot
from telebot import types
import yfinance
import sqlite3
import datetime as dt
import requests as rq
import pandas as pd
import re


# def generate_inline_keyboard (*answer):
#     keyboard = types.InlineKeyboardMarkup()
#     temp_buttons = []
#     for i in answer:
#         temp_buttons.append(types.InlineKeyboardButton(text=i[0], callback_data=i[1]))
#     keyboard.add(*temp_buttons)
#     return keyboard
#
#
# keyboard = generate_inline_keyboard(['Ввести активы', 'input_actives'],
#                                     ['Текущий портфель', 'current_portfolio']
#                                     )

today = dt.datetime.today()

conn = sqlite3.connect('bot_db', check_same_thread=False)
cursor = conn.cursor()


def save_user_data(user_id: int, user_name: str, user_surname: str, username: str):
    cursor.execute('insert into user_data (user_id, user_name, user_surname, username) values (?, ? , ?, ?)',
                   (user_id, user_name, user_surname, username))
    conn.commit()


def add_portfolio(user_id: int, ticker: str, count: int):
    cursor.execute('insert into registry (user_id, ticker, count) values (?, ?, ?)',
                   (user_id, ticker, count))
    conn.commit()


token = 'token'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message, res=False):
    bot.send_message(message.chat.id,
                     "Привет! Данный бот предназначен для портфельной аналитики и выдаче рекомендаций по диверсификации портфеля")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = types.KeyboardButton("Ввести активы")
    item2 = types.KeyboardButton("Текущий портфель")

    markup.add(item1)
    markup.add(item2)

    bot.send_message(message.chat.id,
                     'Нажми: \nВвести активы  - для ввода своего портфеля\nТекущий портфель - для просмотра текущего портфеля',
                     reply_markup=markup)

    us_id = message.from_user.id
    cursor.execute('select * from user_data')
    if us_id not in [x[0] for x in cursor.fetchall()]:
        us_name = message.from_user.first_name
        us_sname = message.from_user.last_name
        username = message.from_user.username

        save_user_data(us_id, us_name, us_sname, username)


@bot.message_handler(content_types=["text"])
def handle_text(message):

    if message.text.strip() == 'Ввести активы':
        print('button work')
        bot.send_message(message.chat.id, "Введи тикер акции и количество через пробел")

    elif message.text.strip() == 'Текущий портфель':

        cursor.execute(f'select ticker, sum(count) from registry where user_id = {message.from_user.id} group by ticker ')

        for t, c in cursor.fetchall():
            print(t, c)
            bot.send_message(message.chat.id, f'{t} - {c}')

    elif message.text.strip().split()[0] in all_stocks_data['symbol'].values and message.text.strip().split()[1].isdigit():
        print('condition works')
        add_portfolio(message.from_user.id, message.text.strip().split()[0], int(message.text.strip().split()[1]))

@bot.callback_query_handler(func=lambda call: True)
def ans(call):
    try:
        message = call.message
        if call.data == 'input_actives':
            bot.send_message(message.chat.id, "Введи тикер бумаги")
        elif call.data == 'current_portfolio':
            pass
    except:
        pass


if __name__ == '__main__':
    data = pd.read_json('https://iss.moex.com/iss/securities.json')
    print(pd.DataFrame(data=data.loc['data'].values[0],
                       columns=data.loc['columns'].values[0]))


    def get_median(lst):
        l = len(lst)
        lst.sort()
        if l % 2 == 0:
            return (lst[l // 2] + lst[l // 2 - 1]) / 2
        else:
            return lst[(l - 1) // 2]
    print(get_median([5, 2, 1, 3, 4]),
get_median([3, 3, 7, 9]))



    #print(rq.get('https://iss.moex.com/iss/securities.csv').content)


    #bot.polling(none_stop=True, interval=0)

