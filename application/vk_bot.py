from random import randrange
from application import vkinder, config
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api

vk = vk_api.VkApi(token=config.GROUP_TOKEN)
session = vk.get_api()
longpoll = VkLongPoll(vk)
pairs_found = []
users_extend_info = []


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


def vk_bot():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                # в боте указано, что для начала работы нужно написать 'hi'
                request = event.text
                if event.user_id in users_extend_info:
                    seeker.set_city(event.text)
                    users_extend_info.remove(event.user_id)
                    seeker.search()
                    write_msg(event.user_id, f"Great, if you wanna find pair in this city say 'yes'")

                elif request.lower() == 'hi':
                    seeker = vkinder.VKinder(event.user_id)
                    if seeker.check_seeker_id():
                        # если уже был, продолжается работа с уже созданной бд
                        write_msg(event.user_id,
                                  f"Hello, my friend! Glad to see you again! Wanna continue? Say 'yes' ))")
                        write_msg(event.user_id, '5 - change city\n6 - exit')
                    else:
                        seeker.search()
                        write_msg(event.user_id,
                                  f"Hi, {seeker.name}. If you wanna find pair in your city say 'yes'")
                        write_msg(event.user_id, '5 - change city\n6 - exit')

                elif request.lower() == 'yes':
                    pairs = seeker.take_from_bd()
                    pairs_found.append(event.user_id)
                    write_msg(event.user_id, f"Many pairs for you were found. Say 'next' to continue")

                elif (request.lower() == '1' or request.lower() == 'next') and event.user_id in pairs_found:
                    pair_id, pair_name, link, top_photo = next(pairs)
                    attachment = ','.join([f'photo{pair_id}_' + i for i in top_photo.split(',')])
                    message = f"Do you like {pair_name}? {link}"
                    vk.method('messages.send',
                              {'user_id': event.user_id, 'message': message, 'random_id': randrange(10 ** 7),
                               'attachment': attachment})
                    write_msg(event.user_id,
                              '1 - next\n2 - to favorite\n3 - see favorite\n4 - to black list\n5 - change city\n6 - exit')
                elif request == '2':
                    seeker.to_favorite(pair_id)
                    write_msg(event.user_id, "Added to favorites")
                    write_msg(event.user_id,
                              '1 - next\n3 - see favorite\n5 - change city\n6 - exit')
                elif request == '3':
                    favorites = seeker.view_favorites()
                    write_msg(event.user_id, "Favorites:")
                    for favorite in favorites:
                        write_msg(event.user_id, f"{favorite}")
                    write_msg(event.user_id, '1 - next\n5 - change city\n6 - exit')
                elif request == '4':
                    seeker.to_blacklist(pair_id)
                    write_msg(event.user_id, "Added to black list")
                    write_msg(event.user_id,
                              '1 - next\n3 - see favorite\n5 - change city\n6 - exit')
                elif request == '5':
                    users_extend_info.append(event.user_id)
                    write_msg(event.user_id, "Where are you from?")
                elif request == "bye" or request == '6':
                    write_msg(event.user_id, "Goodbye, see u")
                else:
                    write_msg(event.user_id, "I don't understand you :(")
