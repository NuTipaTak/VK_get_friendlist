import urllib3
import requests
import csv
import json
from typing import Union
from datetime import datetime


class VKFriends:
    count: int = -1
    items: Union[list[int], list[dict[str, any]]]
    def __init__(self):
        self.items = []

def start() ->VKFriends:
    print("Введите входную информацию")
    token = input("Введите авториризационный токен: ")
    user_id = input("Введите ID пользователя, для которого генерируем отчет: ")
    path = str(input("Введите путь к выходному файлу. По умолчанию — файл с именем report в текущей директории :"))
    format = input("Выберите формат выходног файла \n1 - CVS\n2 - TSV\n3 - JSON\nВведите номер формата: ")
    if format != '':
        if int(format) < 1 or int(format) > 3:
            print("формат выбран не правильно!")
            return

    get_friends(user_id = user_id,access_token = token)

    if VKFriends.count == -1:
        print("Ошибка: вы ввели неправельный авторизационный токен.")
        return

    if path == '' and format == '':
        output()
    elif path == '':
        output(format = format)
    elif format == '':
        output(path = path)
    else:
        output(format = format, path = path)


def get_friends(
    access_token, user_id: int , count: int = 5000, offset: int = 0,
    domain: str = "https://api.vk.com/method", v = "5.124"
    ) -> VKFriends:

    query = f"{domain}/friends.get?access_token={access_token}&user_id={user_id}&fields=bdate, sex, city, country&v={v}&order=name"
    response = requests.get(query).json()
    if 'error' in response:
        print(response['error']['error_msg'])
        return
    VKFriends.items = response['response']['items']
    VKFriends.count = response['response']['count']
    i = 0
    while (i < VKFriends.count):
        del VKFriends.items[i]['id']
        del VKFriends.items[i]['track_code']
        del VKFriends.items[i]['can_access_closed']
        del VKFriends.items[i]['is_closed']
        VKFriends.items[i].update({'first_name': VKFriends.items[i].pop('first_name')})
        VKFriends.items[i].update({'last_name': VKFriends.items[i].pop('last_name')})
        if 'country' in VKFriends.items[i]:
            VKFriends.items[i]['country'] = VKFriends.items[i]['country']['title']
            VKFriends.items[i].update({'country': VKFriends.items[i].pop('country')})

        if 'city' in VKFriends.items[i]:
            VKFriends.items[i]['city'] = VKFriends.items[i]['city']['title']
            VKFriends.items[i].update({'city': VKFriends.items[i].pop('city')})

        if 'bdate' in VKFriends.items[i]:
            if VKFriends.items[i]['bdate'].count('.') == 2:
                VKFriends.items[i]['bdate'] = datetime.strptime(VKFriends.items[i]['bdate'], "%d.%m.%Y")\
                    .strftime("%Y.%m.%d")
            elif VKFriends.items[i]['bdate'].count('.') == 1:
                VKFriends.items[i]['bdate'] = datetime.strptime(VKFriends.items[i]['bdate'], "%d.%m")\
                    .strftime("%m.%d")
            VKFriends.items[i].update({'bdate': VKFriends.items[i].pop('bdate')})

        if 'sex' in VKFriends.items[i]:
            if VKFriends.items[i]['sex'] == 1:
                VKFriends.items[i]['sex'] = 'female'
            elif VKFriends.items[i]['sex'] == 2:
                VKFriends.items[i]['sex'] = 'male'
            VKFriends.items[i].update({'sex': VKFriends.items[i].pop('sex')})
        i += 1

def output(format: int = 1, path: str = 'report') -> VKFriends:

    fields = {'first_name': 'Имя', 'last_name': 'Фамилия', 'country': 'Страна', 'city': 'Город',
              'bdate': 'Дата рождения', 'sex': 'Пол'}
    if int(format) == 1:
        with open(path + '.csv', 'wt', newline='', encoding='utf-8-sig') as state_file:
            writer = csv.DictWriter(state_file, fields.keys(), restval='Unknown', extrasaction='ignore')
            writer.writerow(fields)
            writer.writerows(VKFriends.items)
    elif int(format) == 2:
        with open(path + '.tsv', 'wt', newline='', encoding='utf-8-sig') as state_file:
            writer = csv.DictWriter(state_file, fields.keys(), restval='Unknown', extrasaction='ignore',dialect='excel-tab')
            csv.Dialect.delimiter = '\n'
            writer.writerow(fields)
            writer.writerows(VKFriends.items)
    elif int(format) == 3:
        with open(path + '.json', 'wt') as state_file:
            json.dump(VKFriends.items, state_file,indent=2)

start()








