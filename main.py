from telebot import types, TeleBot
from telebot.types import *
from sqlite3 import connect


bot = TeleBot(token='5314538945:AAGurlaBMqcoOxeKk2yrMUABvDOc_c_3LK4')

keyb1 = types.ReplyKeyboardMarkup(row_width=2)
keyb1.add(KeyboardButton('Настройки'), KeyboardButton('Информация'))
keyb1.add(KeyboardButton('Donation Alerts (пожертвование)'), KeyboardButton('Показать игры по настройкам'))

keyb2 = ReplyKeyboardMarkup(row_width=2)
keyb2.add(KeyboardButton('Процент скидки'))
keyb2.add(KeyboardButton('Желаемое'), KeyboardButton('Назад'))

keyb3 = ReplyKeyboardMarkup(row_width=2)
keyb3.add(KeyboardButton('Добавить'), KeyboardButton('Удалить'))
keyb3.add(KeyboardButton('Назад'))

keyb4 = ReplyKeyboardMarkup(row_width=2)
keyb4.add(KeyboardButton('Action'), KeyboardButton('Adventure'), KeyboardButton('Casual'), KeyboardButton('RPG'),
          KeyboardButton('Strategy'))
keyb4.add(KeyboardButton('Indie'), KeyboardButton('Massively Multiplayer'), KeyboardButton('Racing'),
          KeyboardButton('Simulation'))
keyb4.add(KeyboardButton('Назад'))

price = 0
discount = 0
desired = []


@bot.message_handler(commands=['start'])
def start(message):
    conn = connect("Common/steam.db")

    bot.send_message(message.chat.id, 'Steam_bot к вашим услугам...', reply_markup=keyb1)
    id = message.from_user.id

    cursor = conn.execute("SELECT * FROM users WHERE id = ?", [id])
    if not cursor.fetchall():
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?)", [id, 0, 0, ""])
        conn.commit()


@bot.message_handler(content_types=['text'])
def process_message(message):
    if message.text == "Информация":
        conn = connect("Common/steam.db")
        id = message.from_user.id
        cursor = conn.execute("SELECT Price FROM users WHERE Id = ?", [id])
        discs1 = cursor.fetchall()
        discs1 = str(discs1).replace("[", '')
        discs1 = str(discs1).replace("(", '')
        discs1 = str(discs1).replace(",", '')
        discs1 = str(discs1).replace("]", '')
        discs1 = str(discs1).replace(")", '')
        cursor = conn.execute("SELECT Discount FROM users WHERE Id = ?", [id])
        discs2 = cursor.fetchall()
        discs2 = str(discs2).replace("[", '')
        discs2 = str(discs2).replace("(", '')
        discs2 = str(discs2).replace(",", '')
        discs2 = str(discs2).replace("]", '')
        discs2 = str(discs2).replace(")", '')
        cursor = conn.execute("SELECT Desired FROM users WHERE Id = ?", [id])
        desired = cursor.fetchone()[0].split(";")[1:]
        print(desired)
        # desired = desired.replace('None,', '')
        # desired = desired.replace(',', ';')
        # desired = desired.replace("'", '')
        conn.commit()
        bot.send_message(message.chat.id,
                         'Процент скидки от которого вам будет приходить оповещение о такой скидке на желаемые жанры ' + str(
                             discs2) + '%')
        bot.send_message(message.chat.id, 'Ваши желаемые жанры: ' + ", ".join(desired))
    elif message.text == 'Настройки':
        bot.send_message(message.chat.id, 'Настройки открыты', reply_markup=keyb2)
    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Вы перенесены', reply_markup=keyb1)
    elif message.text == 'Цена':
        message = bot.send_message(message.chat.id,
                                   'Введите цену (в рублях) от которой вам будет отправляться оповещение о 100% скидке на игру (ответь только цифрами)')
        bot.register_next_step_handler(message, save_price)
    elif message.text == "Процент скидки":
        bot.send_message(message.chat.id,
                         'Введите процент скидки (знак процента использовать не надо, просто цифры) от которого вам будет приходить оповещение о такой скидке на желаемые жанры')
        bot.register_next_step_handler(message, save_discount)
    elif message.text == "Желаемое":
        bot.send_message(message.chat.id, ' Выбери действие ', reply_markup=keyb3)
    elif message.text == "Добавить":
        bot.send_message(message.chat.id, ' Добавь жанр (название вбивай точно и без кавычек) жанры на выбор',
                         reply_markup=keyb4)
        bot.register_next_step_handler(message, save_desired)
    elif message.text == "Показать игры по настройкам":  # S.find(str, [start],[end])	#S.rfind(str, [start],[end])
        conn = connect("Common/steam.db")
        id = message.from_user.id
        cursor = conn.execute("SELECT Desired FROM users WHERE Id = ?", [id])
        genres = cursor.fetchone()[0].split(";")
        # print(genres)

        user_suitable_games = set()

        for i in genres:
            if i:
                # print(i)
                cursor1 = conn.execute("SELECT * FROM games where genres = ?", [i])
                for game in cursor1.fetchall():
                    user_suitable_games.add(game)

        user_discount = int(conn.execute("SELECT Discount FROM users WHERE Id = ?", [id]).fetchone()[0])
        print(user_discount)

        answer = []

        sended_games = ""

        for i in user_suitable_games:
            if user_discount >= int(i[3]):
                answer.append(i)
                sended_games += str(i[0]) + "\n"

        counter = 0

        cursor = conn.execute("select sended_games from users where id = ?", [id])
        sended_games = cursor.fetchone()[0]

        sending = []
        # print("initial", sended_games)
        if len(user_suitable_games) > 10:
            for game in user_suitable_games:
                if counter == 10:
                    break
                else:
                    if str(game[0]) not in sended_games:
                        # print(game[0], sended_games.replace('\n', '_'))
                        bot.send_message(message.chat.id, f"Игра - {game[1]}\n"
                                                          f"Цена была - {game[4]}\n"
                                                          f"Цена стала - {game[5]}\n"
                                                          f"Скидка - {game[3]}%\n"
                                                          f"Ссылка на игру в Steam - {game[11]}\n")
                        sended_games += str(game[0]) + "\n"
                        conn.execute("UPDATE users SET sended_games = ? WHERE id = ?", [sended_games, id])
                        conn.commit()
                        counter += 1
                    else:
                        sending.append([game[0]])
        else:
            for game in user_suitable_games:
                bot.send_message(message.chat.id, f"Игра - {game[1]}\n"
                                                  f"Цена была - {game[4]}\n"
                                                  f"Цена стала - {game[5]}\n"
                                                  f"Скидка - {game[3]}%\n"
                                                  f"Ссылка на игру в Steam - {game[11]}\n")
                sended_games += str(game[0]) + "\n"
                conn.execute("UPDATE users SET sended_games = ? WHERE Id = ?", [sended_games, id])
                conn.commit()
                counter += 1
        conn.close()

        if counter == 0:
            bot.send_message(message.chat.id, "Пока что нам нечего вам предложить, мы обязательно напишем вам, когда в Steam появятся новые игры со скидкой")

    elif message.text == "Удалить":
        bot.send_message(message.chat.id, ' Удалить жанр (название вбивай точно и без кавычек) ', reply_markup=keyb4)
        bot.register_next_step_handler(message, del_desired)  # Donation Alerts (пожертвование)
    elif message.text == "Donation Alerts (пожертвование)":
        bot.send_message(message.chat.id, ' https://www.donationalerts.com/r/glebzzzik ')


def save_price(message):  # message.text
    conn = connect("Common/steam.db")
    id = message.from_user.id
    cursor = conn.execute("UPDATE users SET Price = ? WHERE Id = ? ", [int(message.text), id])
    bot.send_message(message.chat.id, 'Цена обновлена ')
    conn.commit()


def save_discount(message):  # message.text
    conn = connect("Common/steam.db")
    id = message.from_user.id
    cursor = conn.execute("UPDATE users SET Discount = ? WHERE Id = ? ", [int(message.text), id])
    bot.send_message(message.chat.id, 'Процент обновлён ')
    conn.commit()  # desired


def save_desired(message):  # message.text
    if str(message.text) == 'Назад':
        bot.send_message(message.chat.id, 'Вы перенесены', reply_markup=keyb1)
    else:
        conn = connect("Common/steam.db")
        id = message.from_user.id
        cursor = conn.execute("SELECT Desired FROM users WHERE Id = ?", [id])
        old_desired = list(cursor.fetchone())
        desired = str(old_desired[0]) + ";" + str(message.text)
        desired = desired.strip()
        desired = desired.replace('None,', '')
        conn.commit()
        conn.execute("UPDATE users SET Desired = ? WHERE Id = ?", [str(desired), id])
        bot.send_message(message.chat.id, 'Жанр добавлен ', reply_markup=keyb3)
        conn.commit()  # desired


def del_desired(message):  # message.text
    conn = connect("Common/steam.db")
    id = message.from_user.id
    cursor = conn.execute("SELECT Desired FROM users WHERE Id = ?", [id])
    old_desired = list(cursor.fetchone())
    desired = str(old_desired[0])
    desired = desired.replace('None,', '')
    desired = desired.replace(str(message.text) + ',', '')
    desired = desired.replace(str(message.text) + ';', '')
    desired = desired.replace(str(message.text), '')
    desired = desired.replace(',', ';')
    desired = desired.strip()
    conn.commit()

    conn.execute("UPDATE users SET Desired = ? WHERE Id = ?", [str(desired), id])
    bot.send_message(message.chat.id, 'Жанр удален', reply_markup=keyb3)
    conn.commit()  # desired


bot.polling()
