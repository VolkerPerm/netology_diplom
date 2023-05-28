from datetime import datetime
from pprint import pprint

import vk_api

from config import acces_token
from data_store import checked


class VkTools():
    def __init__(self, acces_token):
        '''Инициализация'''
        self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):
        '''Выгрузка информации по профилю'''
        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city, bdate, sex, relation, home_town'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'] if 'sex' in info else 0,
                     'city': info['city']['id'] if 'city' in info else 0,
                     'offset': 0
                    }
        return user_info

    def search_users(self, params, offset):
        '''Поиск кандидатов'''


        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5



        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'id_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []

        res = []

        for user in users:
            if user['is_closed'] == False:
                if checked(params['id'], user['id']) == True:
                    res.append({'id': user['id'],
                                'name': user['first_name'] + ' ' + user['last_name']
                                })

        return res

    def get_photos(self, user_id):
        '''Загрузка фотографии'''
        photos = self.api.method('photos.get',
                                {'user_id': user_id,
                                'album_id': 'profile',
                                'extended': 1
                                }
                                )

        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count']
                        }
                        )

        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res

    def search_cities(self, city):
        '''Поиск id города'''
        info_city = self.api.method("database.getCities",
                                   {'items': 0,
                                    'count': 1,
                                    'offset': 0,
                                    'id': 0,
                                    'q': city}
                                )
        items_city = info_city['items']
        for item_c in items_city:
            id_user_city = item_c['id']

            return id_user_city



if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(199494788)
    # pprint(params)
    # print(bot.search_cities("Пермь"))

    users = bot.search_users(params)
    pprint(users)
    pprint(bot.get_photos(users[2]['id']))