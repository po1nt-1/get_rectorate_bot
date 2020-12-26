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
