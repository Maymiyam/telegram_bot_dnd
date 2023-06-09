import telebot
from telebot.types import CallbackQuery

api_token = '5909750312:AAHdJ9vioVLfx58WWvdHZaZ79g-bsUz6bk8'

# иницииализируем бота
bot = telebot.TeleBot(api_token)

# глобальные переменные
character_data = {}
classes = ["Воин", "Варвар", "Паладин", "Монах", "Плут", "Следопыт", "Волшебник", "Чародей", "Колдун", "Бард", "Жрец", "Друид", "Изобретатель"]
parameters = ['Имя', 'Раса', 'Класс', 'Опыт', 'Уровень', 'Сила', 'Ловкость', 'Телосложение', 'Интеллект', 'Мудрость', 'Харизма', 'Максимальное ХР', 'Скорость', 'Класс брони']


def calculate_modifier(value):
    modifier = (int(value) - 10) // 2
    return modifier

# создаем приветствие бота c кнопками 
@bot.message_handler(commands=['start'])
def start_message(message):
    # клавиатура с выбором действий
    bot.send_message(message.chat.id,"Здесь ты сможешь удобно управлять своим D&D персонажем.")
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    create_hero_button = telebot.types.KeyboardButton('Создать лист персонажа')
    play_hero_button = telebot.types.KeyboardButton('Играть персонажем')
    markup.add(create_hero_button, play_hero_button)
    bot.send_message(message.chat.id, "⬇️ Выбери, что хочешь сделать, нажав кнопку ниже.", reply_markup=markup)


# Выбор СОЗДАТЬ ЛИСТ ПЕРСОНАЖА
@bot.message_handler(func=lambda message: message.text == 'Создать лист персонажа')

# ЭТАП 1: имя, класс, раса, опыт, проверка 1

# запрос имени персонажа
def create_character(message):

    bot.send_message(message.chat.id, f'<b>Начнем с имени ✔</b> \n \n' \
                                      f'Имя твоего альтер эго, может быть любым, но для погружения в отыгрыш рекомендуется использовать имена свойственные расе персонажа, или окружения в котором он был воспитан.', parse_mode='HTML')
    bot.send_message(message.chat.id, 'Как зовут твоего персонажа?')

    bot.register_next_step_handler(message, get_class)


# запрос класса
def get_class(message):
    global classes
    global character_data
    
    name = message.text
    character_data['Имя'] = name

    inline_markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    inline_markup.add(*[telebot.types.InlineKeyboardButton(c, callback_data=c) for c in classes])
    
    bot.send_message(message.chat.id, f'<b>Теперь выбери класс.</b> \n \n' \
                                      f'От него зависит, какие именно действия сможет предпринять твой персонаж, и какие умения освоить. Классы условно делятся на 3 основных типа:\n' \
                                      f'💪 Сильные — Воин, Варвар;\n' \
                                      f'💫 Заклинатели — Волшебник, Чародей.\n' \
                                      f'А также их всевозможные смешения — Бард, Монах, Изобретатель и пр.', parse_mode='HTML')
    bot.send_message(message.chat.id, f'⬇️ Выбери класс персонажа:', reply_markup=inline_markup)
    

# обработка inline клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def process_class_step(call):

    global character_data
    chosen_class = call.data
    character_data['Класс'] = chosen_class

    bot.reply_to(call.message, f'Выбранный класс: {chosen_class}')
    get_race(call.message)

@bot.message_handler(func=lambda message: True)
def get_race(message):
    bot.send_message(message.chat.id, f'<b>Супер! А какую расу ты выбрал?</b> \n \n'
                                      f'От расы зависят всевозможные плюсы, которые получит персонаж. Так, например, человек получит +1 ко всем характеристикам.', parse_mode='HTML')
    bot.send_message(message.chat.id, '<b>Введи расу текстовым сообщением:</b>', parse_mode='HTML')
    bot.register_next_step_handler(message, process_race_step)

# запрос опыта
def process_race_step(message):
    global character_data
    race = message.text
    character_data['Раса'] = race
    bot.send_message(message.chat.id, 'Введи количество опыта персонажа:')
    bot.register_next_step_handler(message, get_experience)

def get_experience(message):
    global character_data
    try:
        experience = int(message.text)
        character_data['Опыт'] = experience

        level = calculate_level(experience)
        character_data['Уровень'] = level
        bot.send_message(message.chat.id, f'Мы рассчитали уровень, исходя из опыта. Твой персонаж на {level} уровне.')
        check_first_info(message)
   
    except ValueError:
        bot.send_message(message.chat.id, 'Некорректное значение опыта. Пожалуйста, введите число.')
        bot.register_next_step_handler(message, get_experience)
    
    
def check_first_info(message):
    
    name = character_data.get('Имя')
    chosen_class = character_data.get('Класс')
    race = character_data.get('Раса')
    experience = character_data.get('Опыт')
    level = character_data.get('Уровень')
    
    bot.send_message(message.chat.id, f'<b>Давай проверим, всё ли верно:</b> \n \n'
                                      f'Имя персонажа - {name}\n'
                                      f'Раса - {race}\n'
                                      f'Класс - {chosen_class}\n'
                                      f'У персонажа {experience} опыта и {level} уровень.\n \n'
                                      f'Проверь, всё ли верно, и мы продолжим.', parse_mode='HTML')
    
    # Отправляем клавиатуру для подтверждения или начала сначала
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    yes_button = telebot.types.KeyboardButton('Все верно')
    no_button = telebot.types.KeyboardButton('Начать сначала')
    markup.add(yes_button, no_button)

    bot.send_message(message.chat.id, 'Выбери действие:', reply_markup=markup)

    # Регистрируем обработчики шагов
    bot.register_next_step_handler_by_chat_id(message.chat.id, check_first_step)


@bot.message_handler(func=lambda message: message.text == 'Все верно' or message.text == 'Начать сначала')
def check_first_step(message):
    if message.text == 'Все верно':
        # переход на следующий этап
        bot.send_message(message.chat.id, 'Отлично! Идем дальше.')
        get_strenght(message)
    elif message.text == 'Начать сначала':
        # начать с начала (с выбора имени)
        bot.send_message(message.chat.id, 'Начнем сначала.')
        create_character(message)

# расчет уровня по количеству опыта
def calculate_level(experience):
    level_table = {
        0: 1, 300: 2, 900: 3, 2_700: 4, 6500: 5, 14000: 6, 23000: 7, 34000: 8, 48000: 9, 64000: 10, 85000: 11, 100000: 12,
        120000: 13, 140000: 14, 165000: 15, 195000: 16, 225000: 17, 265000: 18, 305000: 19, 355000: 20
    }

    for exp, level in level_table.items():
        if int(experience) >= int(exp):
            continue
        return level - 1
    
    return 20  # Если опыт больше максимального значения в таблице

# ЭТАП 2: сила, ловкость, телосложение, интеллект, мудрость, харизма, проверка 2

@bot.message_handler(func=lambda message: message.text == 'Все верно')
def get_strenght(message):
    bot.send_message(message.chat.id, f'Продолжим...\n \n'
                                      f'<b>💪 Введи силу персонажа:</b>', parse_mode='HTML')
    bot.register_next_step_handler(message, get_dexterity)

# обработка силы, запрос ловкости
def get_dexterity(message):
    global character_data
    strength = message.text
    character_data['Сила'] = strength

    bot.send_message(message.chat.id, '🤸‍♀ Введи ловкость персонажа:')
    bot.register_next_step_handler(message, get_constitution)

# обработка ловкости, запрос телосложения
def get_constitution(message):
    global character_data
    dexterity = message.text
    character_data['Ловкость'] = dexterity

    bot.send_message(message.chat.id, '🏋 Что с телосложением?')
    bot.register_next_step_handler(message, get_intelligence)

# обработка телосложения, запрос интеллекта
def get_intelligence(message):
    global character_data
    constitution = message.text
    character_data['Телосложение'] = constitution

    bot.send_message(message.chat.id, '🎓 Какой интеллект у персонажа?')
    bot.register_next_step_handler(message, get_wisdom)

# обработка интеллекта, запрос мудрости
def get_wisdom(message):
    global character_data
    intelligence = message.text
    character_data['Интеллект'] = intelligence

    bot.send_message(message.chat.id, '📚 Введи мудрость персонажа:')
    bot.register_next_step_handler(message, get_charisma)

# обработка мудрости, запрос харизмы
def get_charisma(message):
    global character_data
    wisdom = message.text
    character_data['Мудрость'] = wisdom

    bot.send_message(message.chat.id, 'Ну и, наконец, какая у него харизма? 🗣')
    bot.register_next_step_handler(message, process_charisma_step)

# обработка харизмы, начало проверки
def process_charisma_step(message):
    global character_data
    charisma = message.text
    character_data['Харизма'] = charisma

    # Вывод данных персонажа для проверки
    bot.send_message(message.chat.id, 'Ох, это было тяжело. Но мы скоро закончим.\n\n'
                                      'А пока проверим, всё ли верно в характеристиках:')
    

    # Форматирование данных персонажа для вывода
    strength = character_data['Сила']
    dexterity = character_data['Ловкость']
    constitution = character_data['Телосложение']
    intelligence = character_data['Интеллект']
    wisdom = character_data['Мудрость']
    charisma = character_data['Харизма']

    bot.send_message(message.chat.id, f"💪 Сила - {strength}\n" \
                                      f"🏃 Ловкость - {dexterity}\n" \
                                      f"🏋 Телосложение - {constitution}\n" \
                                      f"🎓 Интеллект - {intelligence}\n" \
                                      f"📚 Мудрость - {wisdom}\n" \
                                      f"🗣 Харизма - {charisma}")
    

   # Создаем reply клавиатуру с двумя кнопками
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    correct_button = telebot.types.KeyboardButton('Все правильно')
    edit_button = telebot.types.KeyboardButton('Изменить данные')
    markup.add(correct_button, edit_button)

    # Отправляем новую клавиатуру
    bot.send_message(message.chat.id, '⬇️ Выбери действие, нажав кнопку ниже.', reply_markup=markup)

    # Регистрируем обработчики шагов
    bot.register_next_step_handler_by_chat_id(message.chat.id, check_second_step)

@bot.message_handler(func=lambda message: message.text == 'Все правильно' or message.text == 'Изменить данные')
def check_second_step(message):
    if message.text == 'Все правильно':
        # переход на следующий этап
        bot.send_message(message.chat.id, 'Супер! Продолжим.')
        get_max_health(message)
    elif message.text == 'Изменить данные':
        # Пользователь хочет исправить данные, перенаправляем на шаг силы
        bot.send_message(message.chat.id, 'Давайте сделаем это снова! <b>Введи силу персонажа:</b>', parse_mode='HTML')
        get_dexterity(message)

# обработка интеллекта, запрос мудрости
def get_max_health(message):
    bot.send_message(message.chat.id, 'Последний рывок! 💔 <b>Какое максимальное ХР у персонажа?</b>', parse_mode='HTML')
    bot.register_next_step_handler(message, get_speed)

def get_speed(message):
    global character_data
    max_health = message.text
    character_data['Максимальное ХР'] = max_health

    bot.send_message(message.chat.id, 'Введи скорость персонажа:')
    bot.register_next_step_handler(message, get_armor)

def get_armor(message):
    global character_data
    speed = message.text
    character_data['Скорость'] = speed

    bot.send_message(message.chat.id, 'А какой у персонажа класс брони?')
    bot.register_next_step_handler(message, check_third_step)

def check_third_step(message):
    global character_data
    armor = message.text
    character_data['Класс доспехов'] = armor

    max_health = character_data['Максимальное ХР']
    speed = character_data['Скорость']
    armor = character_data['Класс доспехов']

# Вывод данных персонажа для проверки №3
    bot.send_message(message.chat.id, 'Финальная проверка! Посмотри на характеристики, все верно?')
    bot.send_message(message.chat.id, f"❤️ Максимальное ХР - {max_health}\n" \
                                      f"🏇 Скорость - {speed}\n" \
                                      f"🛡 Класс брони - {armor}")


# Создаем reply клавиатуру с двумя кнопками
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    finish_button = telebot.types.KeyboardButton('Завершить создание персонажа')
    edit_button = telebot.types.KeyboardButton('Изменить данные')
    keyboard.add(finish_button, edit_button)

    bot.send_message(message.chat.id, 'Проверь, все ли верно. Если да, нажми "Завершить создание персонажа" на кнопках ниже ⬇️', reply_markup=keyboard)

    # Регистрируем обработчики шагов
    bot.register_next_step_handler_by_chat_id(message.chat.id, check_third_confirmation)

@bot.message_handler(func=lambda message: message.text == 'Завершить создание персонажа' or message.text == 'Изменить данные')
def check_third_confirmation(message):
    if message.text == 'Завершить создание персонажа':
        # переход на следующий этап
        bot.send_message(message.chat.id, 'Ура! Создание персонажа окончено.')
        display_character_data(message)

    elif message.text == 'Изменить данные':
        # Пользователь хочет исправить данные, перенаправляем на шаг силы
        bot.send_message(message.chat.id, 'Давай попробуем снова! Введи максимальное ХР персонажа:')
        get_max_health(message)

def display_character_data(message):
    # Получение всех данных персонажа из словаря character_data
    
    name = character_data.get('Имя')
    race = character_data.get('Раса')
    chosen_class = character_data.get('Класс')
    experience = character_data.get('Опыт')
    level = character_data.get('Уровень')
    strength = character_data.get('Сила')
    dexterity = character_data.get('Ловкость')
    constitution = character_data['Телосложение']
    intelligence = character_data['Интеллект']
    wisdom = character_data['Мудрость']
    charisma = character_data['Харизма']
    max_health = character_data['Максимальное ХР']
    speed = character_data['Скорость']
    armor = character_data['Класс доспехов']

    # Формирование сообщения с данными персонажа
    character_info = f"<b>Вот твой лист персонажа:</b>\n\n" \
                     f"Имя: {name}\n" \
                     f"Раса: {race}\n" \
                     f"Класс: {chosen_class}\n" \
                     f"Опыт: {experience}\n" \
                     f"Уровень: {level}\n \n" \
                     f"💪 Сила - {strength} ({calculate_modifier(strength)})\n" \
                     f"🏃 Ловкость - {dexterity} ({calculate_modifier(dexterity)})\n" \
                     f"🏋 Телосложение - {constitution} ({calculate_modifier(constitution)})\n" \
                     f"🎓 Интеллект - {intelligence} ({calculate_modifier(intelligence)})\n" \
                     f"📚 Мудрость - {wisdom} ({calculate_modifier(wisdom)})\n" \
                     f"🗣 Харизма - {charisma} ({calculate_modifier(charisma)})\n \n" \
                     f"❤️ Максимальное ХР - {max_health}\n" \
                     f"🏇 Скорость - {speed}\n" \
                     f"🛡 Класс брони - {armor}"


    # Отправка сообщения с данными персонажа и клавиатуры
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    create_hero_button = telebot.types.KeyboardButton('Создать нового персонажа')
    play_hero_button = telebot.types.KeyboardButton('Играть персонажем')
    markup.add(create_hero_button, play_hero_button)
    bot.send_message(message.chat.id, character_info, parse_mode='HTML', reply_markup=markup)
    bot.send_message(message.chat.id, f'Поздравляю!\n \n' \
                                      f'Теперь ты можешь возвращаться сюда, чтобы играть своим персонажем из любой точки мира и в любое время.\n \n' \
                                      f'<b><i>Да пребудет с тобой мудрость дракона и сила великого воина!</i></b> 🐲', parse_mode='HTML')
    bot.send_message(message.chat.id, "⬇️ Выбери, что хочешь делать дальше, нажав кнопку ниже.", reply_markup=markup)
    


# ЭТАП 3: Игра (изменение параметров)

#  клавиатура после завершения создания персонажа

@bot.message_handler(func=lambda message: message.text == 'Создать нового персонажа')
def create_another_character(message):
    # Код для создания нового листа персонажа
    create_character(message)

@bot.message_handler(func=lambda message: message.text == 'Играть персонажем')
def play_character(message):
    global classes
    if character_data:
        # Если уже есть созданный лист персонажа
        inline_markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        inline_markup.add(*[telebot.types.InlineKeyboardButton(p, callback_data=p) for p in parameters])
        bot.send_message(message.chat.id, 'У тебя уже есть созданный лист персонажа. Что бы ты хотел изменить?', reply_markup=inline_markup)
    else:
        # Если лист персонажа еще не создан
        bot.send_message(message.chat.id, 'У тебя еще нет созданного листа персонажа. Чтобы начать, создай новый лист персонажа.')
        create_character(message)

@bot.callback_query_handler(func=lambda call: True)
def edit_parameter(call):
    global character_data
    if call.data == 'Опыт':
        try:
            experience = int(call.message.text)
            character_data['Опыт'] = experience

            level = calculate_level(experience)
            character_data['Уровень'] = level
            bot.send_message(call.message.chat.id, f'Твой персонаж на {level} уровне.')
            display_character_data(call.message)
   
        except ValueError:
            bot.send_message(call.message.chat.id, 'Некорректное значение опыта. Пожалуйста, введите число.')
            bot.register_next_step_handler(call, edit_parameter)
    
    elif call.data in parameters:
        parameter = call.message.text
        bot.send_message(call.message.chat.id, f'Введи новое значение для изменения параметра {parameter}:')
        bot.register_next_step_handler(call, process_edit_parameter, parameter)
        
def process_edit_parameter(message, parameter):
        value = message.text
        character_data[parameter] = value
        bot.send_message(message.chat.id, f'Параметр {parameter} успешно изменен на {value}.')


bot.polling(none_stop=True)