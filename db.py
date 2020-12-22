from typing import Dict, List

from pymongo import MongoClient

free = True


client = MongoClient()
db = client["db"]
collection = db["get_rectorate_bot"]


def __create(data: List) -> bool:
    '''
    Принудительная перезапись коллекции. Используется только при дебаге
    '''

    global free
    if free:
        free = False

        collection.delete_many({})
        collection.insert_many(data)

        free = True
        return True
    else:
        return False


def daily_insert(data: List):
    client = MongoClient()
    db = client["db"]
    collection = db["get_rectorate_bot"]

    const_position = [const_doc['position']
                      for const_doc in list(
        collection.find({'const': True}))]

    if const_position:
        for doc in data:
            if doc['position'] not in const_position:
                collection.delete_one({'position': doc['position']})
                collection.insert_one(doc)
    else:
        collection.delete_many({})
        collection.insert_many(data)

    del client
    collection = None
    db = None


def insert(data: Dict) -> bool:
    global free
    if free:
        free = False

        if len(list(collection.find({'position': data['position']}))) == 0:
            data.update({'const': True})
            r = collection.insert_one(data)
        else:
            free = True
            return False

        free = True
        return True
    else:
        return False


def edit(position: str, new_field: Dict) -> bool:
    global free
    if free:
        free = False

        data = list(collection.find({'position': position}))
        if len(data) != 1:
            free = True
            return False
        data = data[0]

        for key in list(new_field.keys()):
            if key not in list(data.keys()):
                free = True
                return False

        data.update(new_field)
        data.update({'const': True})

        collection.replace_one({'position': position}, data)

        free = True
        return True
    else:
        return False


def remove(position: str):
    global free
    if free:
        free = False

        if len(list(collection.find({'position': position}))) == 0:
            free = True
            return False

        r = collection.delete_many({'position': position})

        free = True
        return True
    else:
        return False


if __name__ == "__main__":
    data = [{'position': 'Ректор', 'office': 'A930 – A941', 'surname': 'Анисимов', 'name': 'Никита', 'middle_name': 'Юрьевич', 'email': 'rectorat@dvfu.ru', 'phone': '8 (423) 265 24 29; Факс: 8 (423) 243 23 15', 'const': False}, {'position': 'Первый проректор', 'office': 'B 913', 'surname': 'Шушин', 'name': 'Андрей', 'middle_name': 'Николаевич', 'email': 'shushin.an@dvfu.ru', 'phone': '8 (423) 265 22 26', 'const': False}, {'position': 'Аппарат проректора по учебной работе', 'office': 'В 912', 'phone': '8 (423) 265 24 24 (доб. 2890)', 'const': False}, {'position': 'Проректор по научной работе, д.ф.-м.н., доцент', 'office': 'А 1132', 'surname': 'Самардак', 'name': 'Александр', 'middle_name': 'Сергеевич', 'email': 'samardak.as@dvfu.ru', 'phone': '8 (423) 265 22 25', 'const': False}, {'position': 'Проректор по развитию', 'office': 'А 837', 'surname': 'Земцов', 'name': 'Дмитрий', 'middle_name': 'Игоревич', 'email': 'zemtsov.di@dvfu.ru', 'const': False}, {'position': 'Проректор по международным отношениям', 'office': 'А 709', 'surname': 'Панова', 'name': 'Виктория', 'middle_name': 'Владимировна', 'email': 'panova.vvl@dvfu.ru', 'phone': '8 (423) 265 22 32', 'const': False}, {'position': 'Проректор по общим вопросам', 'office': 'B 806', 'surname': 'Кошель', 'name': 'Алексей', 'middle_name': 'Сергеевич', 'email': 'koshel.as@dvfu.ru', 'phone': '8 (423) 265 24 24 (доб. 2130)', 'const': False}, {
        'position': 'Проректор по перспективным проектам и новой инфраструктуре', 'office': 'С 740', 'surname': 'Харисова', 'name': 'Елена', 'middle_name': 'Владимировна', 'email': 'kharisova.evl@dvfu.ru', 'phone': '8 (423) 265 24 24 (доб. 2133)', 'const': False}, {'position': 'Проректор по управлению кампусом', 'office': 'А 712', 'surname': 'Ведяшкин', 'name': 'Максим', 'middle_name': 'Викторович', 'email': 'vedyashkin.mv@dvfu.ru', 'phone': '8 (423) 265 24 24 (доб. 2310)', 'const': False}, {'position': 'Проректор по медицинским вопросам', 'office': 'M 712', 'surname': 'Пак', 'name': 'Олег', 'middle_name': 'Игоревич', 'email': 'pak.oi@dvfu.ru', 'phone': '8 (423) 265 24 24 (доб. 3001)', 'const': False}, {'position': 'Проректор по экономике и финансам', 'office': 'B 815', 'surname': 'Заривной', 'name': 'Николай', 'middle_name': 'Александрович', 'email': 'zarivnoi.nal@dvfu.ru', 'phone': '8 (423) 265 24 24 (доб. 2037)', 'const': False}, {'position': 'Главный бухгалтер', 'office': 'В 707', 'surname': 'Коломеец', 'name': 'Яна', 'middle_name': 'Валерьевна', 'email': 'kolomeetc.iv@dvfu.ru', 'phone': '8 (423) 265 24 24 (доб. 2227)', 'const': False}, {'position': 'Директор по экспертной и аналитической работе', 'office': 'F 730', 'surname': 'Ажимов', 'name': 'Феликс', 'middle_name': 'Евгеньевич', 'phone': '8 (423) 265 24 24 (доб. 2413)', 'const': False}]

    # print(__create(data))
    # print(daily_insert(data))
    # print(insert({'position': 'Новый сотрудник', 'surname': 'Васильев'}))
    # print(edit('Новый сотрудник', {'office': 'под мостом'}))
    # print(remove('Ректор'))
