import json
import multiprocessing as mp
import time
from parser import parser

import requests

import db
from service import Local_Error, path_to


def init_token():
    global token
    with open(path_to('token'), 'r', encoding='utf-8') as f:
        token = f.read()


def bot_request(method, *args):
    url = f'https://api.telegram.org/bot{token}/{method}'
    if args:
        url += '?'
        for arg in args:
            url += f'{arg}&'
        url = url[:-1]

    return requests.get(url).json()


def get_last_obj(offset=None):
    if offset is None:
        r = bot_request('getUpdates').get('result')
    else:
        r = bot_request('getUpdates', f'offset={offset}').get('result')

    if r:
        return r[-1]

    return None


def message_filter(message_obj):
    if message_obj.get('text'):
        message = [word.lower().strip()
                   for word in message_obj['text'].split(' ', 1)]

        if len(message) == 2:
            command = message[0]
            message = message[1]
            if '/worker' in command:
                message_obj['text'] = message
                message_obj.update({'edit': False})
                return message_obj
            if '/edit' in command:
                message_obj['text'] = message
                message_obj.update({'edit': True})
                return message_obj
    return None


def edit_message_handler(row_obj_):
    sieve_1 = row_obj_.get('message')
    if sieve_1:
        sieve_2 = sieve_1.get('reply_to_message')

        if sieve_2 and sieve_1.get('message_id'):
            if sieve_1.get('from') and sieve_1.get('chat') \
                    and sieve_2.get('from') and sieve_2.get('chat') \
                    and sieve_1.get('text') and sieve_2.get('text'):

                if sieve_1['from'].get('id') \
                        and sieve_1['chat'].get('id') \
                        and sieve_2['from'].get('id') \
                        and sieve_2['chat'].get('id'):

                    if sieve_1['chat']['id'] == sieve_2['chat']['id'] \
                        and (sieve_1['text'] == "Вставить"
                             or sieve_1['text'] == "Изменить"
                             or sieve_1['text'] == "Удалить") \
                            and sieve_2['text'] == "Какое действие выполнить?":

                        return {
                            'message_id': sieve_1['message_id'],
                            'user_id': sieve_1['from']['id'],
                            'chat_id': sieve_1['chat']['id'],
                            'text': sieve_1['text']
                        }
    return None


def worker_message_handler(row_obj_):
    sieve_1 = row_obj_.get('message')
    if sieve_1:
        sieve_2 = sieve_1.get('reply_to_message')

        if sieve_2 and sieve_1.get('message_id'):
            if sieve_1.get('from') and sieve_1.get('chat') \
                    and sieve_2.get('from') and sieve_2.get('chat') \
                    and sieve_1.get('text') and sieve_2.get('text'):

                if sieve_1['from'].get('id') \
                        and sieve_1['chat'].get('id') \
                        and sieve_2['from'].get('id') \
                        and sieve_2['chat'].get('id'):

                    if sieve_1['chat']['id'] == sieve_2['chat']['id'] \
                        and (sieve_1['text'] == "Только ФИО"
                             or sieve_1['text'] == "Всё") \
                            and sieve_2['text'] == "Какую информацию вывести?":

                        return {
                            'message_id': sieve_1['message_id'],
                            'user_id': sieve_1['from']['id'],
                            'chat_id': sieve_1['chat']['id'],
                            'text': sieve_1['text']
                        }
    return None


def message_handler(row_obj_):  # TODO: правильно обрабатывать /edit
    message_obj = {}

    sieve = row_obj_.get('message')
    if sieve:
        sieve = sieve.get('entities')
        if sieve:
            if len(sieve) == 1:
                sieve = sieve[0].get('type')
                if sieve == 'bot_command':
                    if sieve:
                        chat = row_obj_['message'].get('chat')
                        text = row_obj_['message'].get('text')
                        from_ = row_obj_['message'].get('from')
                        message_id = row_obj_['message'].get('message_id')
                        if text and chat and from_ and message_id:
                            if chat.get('id'):
                                if from_.get('id'):
                                    if chat['id'] != from_['id']:
                                        message_obj = {'chat_id': chat['id'],
                                                       'user_id': from_['id'],
                                                       'text': text,
                                                       'message_id': message_id
                                                       }
                                        return message_filter(message_obj)

    return None


def task():
    try:
        global thread_data

        start_parsing_time = -99999

        first_step = True
        while True:
            if time.time() - start_parsing_time > 86400:
                start_parsing_time = time.time()
                db.daily_insert(parser())

            if first_step:
                first_step = False
                print('\rЗапущено      ')

    except KeyboardInterrupt:
        return


def show_worker_keyboard(message_obj):
    json_keyboard = json.dumps({
        'keyboard': [["Только ФИО", "Всё"]],
        'one_time_keyboard': True,
        'resize_keyboard': True,
        'selective': True
    })

    r = bot_request('sendMessage',
                    'chat_id=' + str(message_obj['chat_id']),
                    'text=' + str("Какую информацию вывести?"),
                    'reply_markup=' + str(json_keyboard),
                    'reply_to_message_id=' + str(message_obj['message_id'])
                    )


def show_edit_keyboard(message_obj):
    admin_list = bot_request(
        'getChatAdministrators',
        f'chat_id={message_obj["chat_id"]}'
    )
    if admin_list.get('ok'):
        admin_list = [admin['user']['id']
                      for admin in admin_list['result']]
    if message_obj['user_id'] in admin_list:
        print("изменяем данные на",
              message_obj['text'])

    json_keyboard = json.dumps({
        'keyboard': [["Вставить", "Изменить", "Удалить"]],
        'one_time_keyboard': True,
        'resize_keyboard': True,
        'selective': True
    })

    r = bot_request('sendMessage',
                    'chat_id=' + str(message_obj['chat_id']),
                    'text=' + str("Какое действие выполнить?"),
                    'reply_markup=' + str(json_keyboard),
                    'reply_to_message_id=' + str(message_obj['message_id'])
                    )


def long_pool():
    last_uid = 0

    first_step = True
    worker_flag = False
    edit_flag = False

    worker_user_id = 0
    worker_chat_id = 0
    edit_user_id = 0
    edit_chat_id = 0

    requested_doc = {}

    while True:
        if first_step:
            obj_ = get_last_obj()
        else:
            obj_ = get_last_obj(current_uid + 1)

        if not obj_:
            continue

        current_uid = obj_['update_id']

        if current_uid != last_uid:
            last_uid = current_uid
            if first_step:
                first_step = False

            if edit_flag:
                edit_message_obj = edit_message_handler(obj_)
                if edit_message_obj:
                    if worker_user_id == edit_message_obj['user_id'] \
                            and edit_chat_id == edit_message_obj['chat_id']:
                        if edit_message_obj['text'] == 'Вставить':
                            response = 'Введите данные в формате json-словаря. Шаблон: \n' + \
                                '{\n' + \
                                '\t"position": "Поле должности является обязательным",\n' + \
                                '\t"office": "A 101",\n' + \
                                '\t"surname": "Иванов",\n' + \
                                '\t"name": "Иван",\n' + \
                                '\t"middle_name": "Иванович",\n' + \
                                '\t"email": "ivanov.ii@dvfu.ru",\n' + \
                                '\t"phone": "8 (423) 212 34 55 (доб. 2010)"\n' + \
                                '}'

                        elif edit_message_obj['text'] == 'Изменить':
                            response = ''
                        elif edit_message_obj['text'] == 'Удалить':
                            pass
                        else:
                            continue

                        debug = bot_request('sendMessage',
                                            'chat_id=' + str(edit_chat_id),
                                            'parse_mode=HTML',
                                            'text=' + str(response),
                                            'reply_to_message_id=' +
                                            str(edit_message_obj['message_id'])
                                            )
                        edit_flag = False
                        edit_user_id = 0
                        edit_chat_id = 0

            if worker_flag:
                worker_message_obj = worker_message_handler(obj_)
                if worker_message_obj:
                    if worker_user_id == worker_message_obj['user_id'] \
                            and worker_chat_id == worker_message_obj['chat_id']:
                        if worker_message_obj['text'] == 'Только ФИО':
                            response = str(
                                f"<b>Фамилия</b>: {requested_doc['surname']}\n" +
                                f"<b>Имя</b>: {requested_doc['name']}\n" +
                                f"<b>Отчество</b>: {requested_doc['middle_name']}\n"
                            )
                        elif worker_message_obj['text'] == 'Всё':
                            response = ''
                            for key, val in requested_doc.items():
                                if key == 'position':
                                    key = 'Должность'
                                elif key == 'office':
                                    key = 'Кабинет'
                                elif key == 'surname':
                                    key = 'Фамилия'
                                elif key == 'name':
                                    key = 'Имя'
                                elif key == 'middle_name':
                                    key = 'Отчество'
                                elif key == 'email':
                                    key = 'Почта'
                                elif key == 'phone':
                                    key = 'Телефон'
                                else:
                                    continue

                                response += f'<b>{str(key)}</b>: {val}\n'
                            if not response:
                                response = None
                        else:
                            continue

                        debug = bot_request('sendMessage',
                                            'chat_id=' + str(worker_chat_id),
                                            'parse_mode=HTML',
                                            'text=' + str(response),
                                            'reply_to_message_id=' +
                                            str(worker_message_obj['message_id'])
                                            )
                        worker_flag = False
                        worker_user_id = 0
                        worker_chat_id = 0

            message_obj = message_handler(obj_)
            if message_obj:
                data = list(db.collection.find({}))

                requested_doc = None
                if data:
                    for doc in data:
                        position = doc['position'].lower().strip()
                        if position == message_obj['text']:
                            requested_doc = doc
                            break

                if requested_doc:
                    if message_obj['edit']:
                        show_edit_keyboard(message_obj)
                        edit_flag = True
                        edit_user_id = message_obj['user_id']
                        editr_chat_id = message_obj['chat_id']
                    else:
                        show_worker_keyboard(message_obj)
                        worker_flag = True
                        worker_user_id = message_obj['user_id']
                        worker_chat_id = message_obj['chat_id']


def main():
    try:
        print("Запускается...", end='')

        p = mp.Process(target=task)
        p.start()

        init_token()

        long_pool()
    except KeyboardInterrupt:
        pass
    finally:
        p.terminate()
        print("\rОстановлено\t\t")


if __name__ == "__main__":
    main()