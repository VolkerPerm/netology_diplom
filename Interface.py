from datetime import datetime

import vk_api
import sqlalchemy
from sqlalchemy.orm import session, Session
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from data_store import add_bd, create_tables, extraction_bd, engine, Viewed, checked
from config import comunity_token, acces_token
from core import VkTools

class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                               )

    def is_valid_date(self, date):
        try:
            datetime.strptime(date, '%d.%m.%Y')
            return True, date
        except ValueError:
            return False

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        create_tables(engine)

        city_name_s = 'город '

        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()


                if command == 'привет' or command == 'здравствуй' or command == 'здравствуйте':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Приветствую, {self.params["name"]}')
                    self.message_send(event.user_id, f'Для корректной работы советую ввести свою дату рождения в формате ДД.ММ.ГГГГ')
                    if self.params['city'] == 0:
                        self.message_send(event.user_id, f'Введите, пожалуйста, ваш город, например: город Москва')
                    elif self.params['bdate'] == None:
                        self.message_send(event.user_id, f'Введите, пожалуйста, вашу дату рождения в формате ДД.ММ.ГГГГ')
                elif command == 'поиск':
                    if self.params == None:
                        self.message_send(event.user_id, f'Давайте, в начале поздороваемся?')
                    elif self.params['city'] == 0:
                        self.message_send(event.user_id, f'Давайте, в начале поздороваемся?')
                    elif self.params['bdate'] == None:
                        self.message_send(event.user_id, f'Давайте, в начале поздороваемся?')
                    else:
                        users = self.api.search_users(self.params, self.offset)
                        self.offset = self.offset + 51
                        user = users.pop()
                        photos_user = self.api.get_photos(user['id'])

                        attachment = ''
                        for num, photo in enumerate(photos_user):
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                            if num == 2:
                                break
                        self.message_send(event.user_id,
                                          f'Встречайте: {user["name"]} https://vk.com/id{user["id"]}',
                                          attachment=attachment
                                          )
                        add_bd(event.user_id, user['id'])
                        print(users)

                elif city_name_s in command:
                    city_name = command[6:]
                    city_users = self.api.search_cities(city_name)
                    self.params['city'] = city_users
                    self.message_send(event.user_id, f'Данные о городе получены')
                elif len(command.split('.')) == 3:
                    bdate_split = command
                    if self.is_valid_date(bdate_split) == (True, bdate_split):
                        self.api.get_profile_info(event.user_id)['bdate'] = bdate_split
                        self.message_send(event.user_id, f'Данные о дате рождения получены')
                    elif self.is_valid_date(bdate_split) == False:
                        self.message_send(event.user_id, f'Неверно введена дата рождения')

                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'Команда не опознана. Для поиска собеседника наберите слово "поиск".')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
    # print(bot.is_valid_date('17.04.1991'))