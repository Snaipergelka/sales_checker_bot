import telebot
import requests
import os

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


@bot.message_handler(commands=['start', 'help'])
def start_help_messages(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_registrate = telebot.types.InlineKeyboardButton(text='Зарегистрироваться',
                                                        callback_data='registration')
    keyboard.add(key_registrate)
    key_add = telebot.types.InlineKeyboardButton(text='Добавить продукт для отслеживания',
                                                 callback_data='add_subscr')
    keyboard.add(key_add)
    key_show = telebot.types.InlineKeyboardButton(text='Посмотреть мои подписки',
                                                  callback_data='show_subscr')
    keyboard.add(key_show)
    key_unsubscribe = telebot.types.InlineKeyboardButton(text='Отписаться от обновлений продукта',
                                                         callback_data='unsubscribe')
    keyboard.add(key_unsubscribe)
    key_delete_user = telebot.types.InlineKeyboardButton(text='Удалить все свои данные',
                                                         callback_data='delete_user')
    keyboard.add(key_delete_user)
    key_help = telebot.types.InlineKeyboardButton(text='Помощь',
                                                  callback_data='help')
    keyboard.add(key_help)
    key_bye = telebot.types.InlineKeyboardButton(text='Пока!',
                                                 callback_data='bye')
    keyboard.add(key_bye)
    bot.send_message(message.chat.id,
                     'Привет! '
                     'Я бот для отслеживания цены в '
                     'интернет-магазине sephora.ru. '
                     'Выбери, что ты хочешь сделать.',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    if call.data == 'registration':
        bot.send_message(call.message.chat.id, 'Пожалуйста, пришли свое имя.')
        bot.register_next_step_handler(call.message, register_user)

    elif call.data == 'add_subscr':
        bot.send_message(call.message.chat.id, 'Пожалуйста, пришли ссылку на продукт.')
        bot.register_next_step_handler(call.message, subscribe_to_product)

    elif call.data == 'show_subscr':
        keyboard = telebot.types.ReplyKeyboardMarkup()
        key_number = telebot.types.KeyboardButton(text='Поделиться номером телефона',
                                                  request_contact=True)
        keyboard.add(key_number)
        bot.send_message(call.message.chat.id, 'Чтобы увидеть подписки, пожалуйста,'
                                               ' поделись номером телефона.',
                         reply_markup=keyboard)
        bot.register_next_step_handler(call.message, show_subscriptions)

    elif call.data == 'unsubscribe':
        bot.send_message(call.message.chat.id, 'Пожалуйста, пришли ссылку на продукт.')
        bot.register_next_step_handler(call.message, unsubscribe)

    elif call.data == 'delete_user':
        bot.send_message(call.message.chat.id, 'Пожалуйста, пришли свое имя.')
        bot.register_next_step_handler(call.message, delete_user)

    elif call.data == 'bye':
        bot.send_message(call.message.chat.id, 'Спасибо! Хорошего дня!')

    else:
        bot.send_message(call.message.chat.id, 'Нажми /help')


def register_user(message):
    name = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup()
    key_number = telebot.types.KeyboardButton(text='Поделиться номером телефона.',
                                              request_contact=True)
    keyboard.add(key_number)
    bot.send_message(message.chat.id, 'Для продолжения нужно поделиться номером телефона.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, transfer_registration_data_to_api, name)


def transfer_registration_data_to_api(message, name):
    answer = requests.post('http://127.0.0.1:8000/user/registration',
                           json={'name': name,
                                 'phone_number': str(message.contact.phone_number)})
    delete_keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, answer.json()['message'],
                     reply_markup=delete_keyboard)
    send_keyboard(message)


def subscribe_to_product(message):
    url = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup()
    key_number = telebot.types.KeyboardButton(text='Поделиться номером телефона.',
                                              request_contact=True)
    keyboard.add(key_number)
    bot.send_message(message.chat.id, 'А теперь поделись номером телефона.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, transfer_subscription_data_to_api, url)


def transfer_subscription_data_to_api(message, url):
    answer = requests.post('http://127.0.0.1:8000/subscription/subscribe_to_product',
                  json={'url': url,
                        'phone_number': message.contact.phone_number})
    delete_keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, answer.json()["message"],
                     reply_markup=delete_keyboard)
    send_keyboard(message)


def unsubscribe(message):
    url = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup()
    key_number = telebot.types.KeyboardButton(text='Поделиться номером телефона',
                                              request_contact=True)
    keyboard.add(key_number)
    bot.send_message(message.chat.id, 'Чтобы отписаться, пожалуйста,'
                                      ' поделись номером телефона.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, transfer_unsubscription_data_to_api, url)


def transfer_unsubscription_data_to_api(message, url):
    answer = requests.post('http://127.0.0.1:8000/subscription/unsubscribe_product',
                           json={'phone_number': message.contact.phone_number,
                                 'url': url})
    delete_keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, answer.json()["message"],
                     reply_markup=delete_keyboard)
    send_keyboard(message)


def show_subscriptions(message):
    answer = requests.post('http://127.0.0.1:8000/subscription/all_subscribed_products_with_details',
                           json={'phone_number': message.contact.phone_number})
    delete_keyboard = telebot.types.ReplyKeyboardRemove()
    if not answer.text:
        bot.send_message(message.chat.id, 'Ты пока не подписан ни на один продукт.',
                         reply_markup=delete_keyboard)
    bot.send_message(message.chat.id, f'Вот твои подписки: {", ".join(answer.json()["message"])}.',
                     reply_markup=delete_keyboard)
    send_keyboard(message)


def delete_user(message):
    name = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup()
    key_number = telebot.types.KeyboardButton(text='Поделиться номером телефона.',
                                              request_contact=True)
    keyboard.add(key_number)
    bot.send_message(message.chat.id, 'А теперь поделись номером телефона.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, transfer_deletion_data_to_api, name)


def transfer_deletion_data_to_api(message, name):
    answer = requests.delete('http://127.0.0.1:8000/user/delete_user',
                    json={'name': name,
                          'phone_number': message.contact.phone_number})
    delete_keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Все твои данные были успешно удалены!',
                     reply_markup=delete_keyboard)
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_bye = telebot.types.InlineKeyboardButton(text='Пока!',
                                                 callback_data='bye')
    keyboard.add(key_bye)
    bot.send_message(message.chat.id, answer.json()['message'],
                     reply_markup=keyboard)


def send_keyboard(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_add = telebot.types.InlineKeyboardButton(text='Добавить продукт для отслеживания',
                                                 callback_data='add_subscr')
    keyboard.add(key_add)
    key_show = telebot.types.InlineKeyboardButton(text='Посмотреть мои подписки',
                                                  callback_data='show_subscr')
    keyboard.add(key_show)
    key_unsubscribe = telebot.types.InlineKeyboardButton(text='Отписаться от обновлений продукта',
                                                         callback_data='unsubscribe')
    keyboard.add(key_unsubscribe)
    key_delete_user = telebot.types.InlineKeyboardButton(text='Удалить все свои данные',
                                                         callback_data='delete_user')
    keyboard.add(key_delete_user)
    key_help = telebot.types.InlineKeyboardButton(text='Помощь',
                                                  callback_data='help')
    keyboard.add(key_help)
    key_bye = telebot.types.InlineKeyboardButton(text='Пока!',
                                                 callback_data='bye')
    keyboard.add(key_bye)
    bot.send_message(message.chat.id,
                     'Супер! Что бы ты хотел сделать еще?',
                     reply_markup=keyboard)


bot.infinity_polling()
