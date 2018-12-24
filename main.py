from flask import Flask, request
from flask_sslify import SSLify
from pymessenger.bot import Bot
import requests
import random
import config
import json

app = Flask(__name__)
id_app = '329898244220560'

bot = Bot(config.TOKEN)

# список user
users = {}
URL = 'https://api.telegram.org/bot{}'.format(config.TOKEN)

# список привествий
greeating = ['привет','добрый день','добрый вечер','здравствуйте']
num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# доплнительные функции!!
def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return

def check_number_phone(text):
    text_len = len(text)
    if text_len != 11:
        return False
    else:
        i = 0
        sum = 0
        while i != text_len:
            if (str(text[i]) in num) == False:
                return False
            i += 1
        return True

def verify_fb_token(token_sent):
    '''Сверяет токен, отправленный фейсбуком, с имеющимся у вас.
    При соответствии позволяет осуществить запрос, в обратном случае выдает ошибку.'''
    if token_sent == config.VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return 'Invalid verification token'

# обработчик вопросов
# Привет! Данный бот предназначен для сбора контактной информации. Оставь свой номер телефона и в ближайшее время наш оператор с Вами свяжется! Основные правила ввода номера телефона:
# 1. Длина номера телефона равна 11. 2. Номер должен начинаться с 8. 3. В номере телефона должны быть только цифры.

def handler_question(id, text):
    text_lower = str(text).lower()

    print('handler_question()')

    if users[id]['level'] == '0':
        if (text_lower in greeating) == False:
            text = 'Для начала давай поприветствуем друг друга!'
            bot.send_text_message(id, text)
            users[id]['level'] = '0'
        else:
            text = 'Привет! Данный бот предназначен для сбора контактной информации.\nОставь свой номер телефона ' \
                   'и в ближайшее время наш оператор с Вами свяжется!\n' \
                   'Основные правила ввода номера телефона:\n' \
                   '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 8.' \
                   '\n3. В номере телефона должны быть только цифры.'
            bot.send_text_message(id, text)
            users[id]['level'] = '1'
    elif users[id]['level'] == '1' or users[id]['level'] == '2':
        if text[0] != 8 and len(text) == 10:
            text = 'Номер телефона должен начинаться с 8! Еще раз скажу правила ввода номера:\n' \
                   '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 8.' \
                   '\n3. В номере телефона должны быть только цифры.'
            bot.send_text_message(id, text)
        elif len(text_lower) != 11:
            text = 'Данный бот предназначен для сбора контактной информации.\nПомощь в написании номера телефона:\n1. ' \
                   'Длина номера телефона равна 11.\n2. Номер должен начинаться с 8.' \
                   '\n3. В номере телефона должны быть только цифры.'
            bot.send_text_message(id, text)
        else:
            if text_lower[0] != '8':
                text = 'Номер телефона должен начинаться с 8! Еще раз скажу правила ввода номера:\n' \
                       '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 8.' \
                       '\n3. В номере телефона должны быть только цифры.'
                bot.send_text_message(id, text)
            elif check_number_phone(text_lower) == False:
                text = 'В номере должны присутствовать только цифры. Еще раз скажу правила ввода номера:\n' \
                       '1. Длина номера телефона равна 11.\n2. Номер должен начинаться с 8.' \
                       '\n3. В номере телефона должны быть только цифры.'
                bot.send_text_message(id, text)
            else:
                if users[id]['number_mobile'] == 'no':
                    users[id]['number_mobile'] = text_lower
                    text = 'Ваш номер {} попал в базу. Ждите звонка от нашего оператора!'.format(text)
                    bot.send_text_message(id, text)
                    users[id]['level'] = '2'
                else:
                    text = 'Ваш номер телефона поменялся на - {}'.format(text_lower)
                    users[id]['number_mobile'] = text_lower
                    bot.send_text_message(id, text)
                    users[id]['level'] = '2'

    return

# обработчик всех функций
def handler_funk(id, text):

    print(users)

    if id not in users.keys():
        print('тут!')
        users[id] = {'number_mobile': 'no', 'level':'0'}

    handler_question(id, text)

    return

# Получать сообщения, посылаемые фейсбуком нашему боту мы будем в этом терминале вызова
@app.route('/', methods=['GET', 'POST'])
def index():
    print(request.method, ':')
    if request.method == 'GET':
        # до того как позволить людям отправлять что-либо боту, Facebook проверяет токен,
        # подтверждающий, что все запросы, получаемые ботом, приходят из Facebook
        token_sent = request.args['hub.verify_token']
        return verify_fb_token(token_sent)
    else:
        r = request.get_json()

        if r['entry'][0]['messaging'][0]['sender']['id'] != id_app:
            messaging = r['entry'][0]['messaging'][0]
            if messaging.get('message'):
                id = messaging['sender']['id']
                if messaging['message'].get('text'):
                    text = messaging['message']['text']

                print('--- to (', config.num, ') ---')
                print('chat_id: ', id)
                print('text: ', text)
                handler_funk(id, text)
                print('level: ', users[id]["level"])
                print('number_mobile: ', users[id]["number_mobile"])
                print('-------------------------')

                write_json(r)

                config.num += 1

    return '<h1> Bot welcomes you! </h1>'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')
