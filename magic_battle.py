import datetime
import random
import traceback
from telebot import TeleBot, types
from pymongo import MongoClient
from classes.Battle import Battle
from classes.Spell import compute_spell
from locale import rus

creator = 268486177
bot = TeleBot('870593345:AAHburWChfp5ZmPlFahNnxT9G_6ry6y_yPg')
client = MongoClient('mongodb+srv://interbellum_bot:9ga6kKAhm3zAQmp@cluster0-rnman.gcp.mongodb.net/test?retryWrites=true')
db = client.mags
players = db.players

battles = {}
players_in_game = {}


@bot.inline_handler(func=lambda c: True)
def inline_hndlr(q):
    answers = []
    counter = 0
    if q.from_user.id in players_in_game.keys():
        for preset in players_in_game[q.from_user.id].presets:
            answers.append(types.InlineQueryResultArticle(id=counter, title=preset,
                                                          input_message_content=types.InputTextMessageContent(preset)))
            counter += 1
        bot.answer_inline_query(q.id, answers)


@bot.message_handler(commands=['delall'])
def del_all(m):
    if m.from_user.id == creator:
        players.delete_many({})
        bot.reply_to(m, '✅')


@bot.message_handler(commands=['battle'])
def game(m):
    if m.chat.id in battles:
        return
    battles[m.chat.id] = Battle({})
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Присоедениться', url='t.me/new_amber_bot?start={}'.format(m.chat.id)))
    bot.send_message(m.chat.id, 'Начался подбор в игру! для регистрации нажмите на кнопку ниже...', reply_markup=kb)


@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.type == 'private':
        if not players.find_one({'id': m.from_user.id}):
            bot.send_message(m.chat.id, 'Добро пожаловать в игру! В будущем это будет игра по мотивам книги Роджера '
                                        'Желязны "Хроники Амбера", а сейчас это просто драка магов. Следите за новостями.\n'
                                        'Как вас называть милорд? (русские буквы, 4-10 символов)')
            bot.register_next_step_handler_by_chat_id(m.chat.id, set_name)
            players.insert_one(new_player(m.from_user.id))
            return
        try:
            chat = int(m.text.split()[1])
            player = players.find_one({'id': m.from_user.id})
            res = battles[chat].add_player(player)
        except Exception as e:
            bot.send_message(m.chat.id, traceback.format_exc())
            return
        if res:
            bot.send_message(m.chat.id, 'Вы присоеденились к игре')
            bot.send_message(chat, 'К игре присоеденился {}'.format(m.from_user.first_name))
        if not res:
            bot.send_message(m.chat.id, 'Что-то пошло не так')


def set_name(m):
    if m.text.isnumeric() or len(m.text) < 4 or len(m.text) > 10:
        bot.send_message(m.chat.id, 'русские буквы, 4-10 символов')
        bot.register_next_step_handler_by_chat_id(m.chat.id, set_name)
        return
    players.update_one({'id': m.chat.id}, {'$set': {'name': m.text}})
    bot.send_message(m.chat.id, 'Хорошо, {}'.format(m.text))
    send_menu(m.chat.id)


@bot.message_handler(commands=['go'])
def s(m):
    if m.chat.id not in battles:
        return
    next_id, next_name = battles[m.chat.id].start()
    text = ''
    for mag in battles[m.chat.id].mags.values():
        text += '<b>{}</b>: {}♥️\n'.format(mag.name, mag.hp)
        players_in_game[mag.id] = mag
    text += 'Игра началась! Первый ходит {}'.format(next_name)
    bot.send_message(m.chat.id, text, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.chat.type == 'private')
def private_handler(m):
    if m.text == '🔮Пресеты':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton('🔮👁‍🗨Посмотреть'))
        kb.add(types.KeyboardButton('🔮➕Добавить'))
        kb.add(types.KeyboardButton('🔮➖Удалить'))
        kb.add(types.KeyboardButton('↩️Назад'))
        bot.send_message(m.chat.id, 'Выберите действие', reply_markup=kb)
    if m.text == '🔮👁‍🗨Посмотреть':
        text = 'Ваши пресеты: \n\n'
        counter = 1
        for preset in players.find_one({'id': m.from_user.id}, {'presets': 1})['presets']:
            text += '{}. {}\n'.format(counter, preset)
            counter += 1
        if counter == 1:
            text = 'У вас нет пресетов'
        bot.send_message(m.chat.id, text)
    if m.text == '🔮➕Добавить':
        bot.send_message(m.chat.id, 'Введите текст для пресета...')
        bot.register_next_step_handler_by_chat_id(m.chat.id, text_preset)
    if m.text == '🔮➖Удалить':
        bot.send_message(m.chat.id, 'Введите номер пресета, который хотите удалить...')
        bot.register_next_step_handler_by_chat_id(m.chat.id, del_preset)
    if m.text == '↩️Назад':
        send_menu(m.chat.id)


def del_preset(m):
    try:
        players.update_one({'id': m.from_user.id},
                           {'$unset': {'presets.{}'.format(int(m.text)-1): ''}})
        players.update_one({'id': m.from_user.id}, {'$pull': {'presets': None}})
    except:
        bot.send_message(m.chat.id, 'Нет такого номера')
        print(traceback.format_exc())
    else:
        bot.send_message(m.chat.id, 'Успешно!')
    send_menu(m.from_user.id)


spells = {}
def text_preset(m):
    spell = compute_spell(m.text)
    text = ''
    if spell.type == 'damage':
        text += 'Урон: {}\n'.format(spell.damage)
    elif spell.type == 'heal':
        text += 'Хил: {}\n'.format(spell.heal)
    text += 'Тип: {}\n'.format(rus(spell.type))
    text += 'Область: {}\n'.format(rus(spell.area))
    text += 'Накладывает эффекты: \n'
    for effect in spell.with_effects:
        text += rus(effect) + '\n'
    kb = types.ReplyKeyboardMarkup()
    btn_yes = types.KeyboardButton('✅Подтверждаю')
    btn_no = types.KeyboardButton('❌Отмена')
    kb.add(btn_yes, btn_no)
    bot.send_message(m.chat.id, text, reply_markup=kb)
    spells[m.from_user.id] = m.text
    bot.register_next_step_handler_by_chat_id(m.chat.id, last_step_add_preset)


def last_step_add_preset(m):
    if m.text == '✅Подтверждаю':
        players.update_one({'id': m.from_user.id}, {'$push': {'presets': spells[m.from_user.id].lower()}})
    spells.pop(m.from_user.id)
    send_menu(m.from_user.id)


@bot.message_handler(content_types=['text'])
def hndl(m):
    if m.chat.id in battles and battles[m.chat.id].status == 'start':
        if m.from_user.id in battles[m.chat.id].mags:
            res, next_mag = battles[m.chat.id].cast(m.from_user.id, m.text.lower())
            if res:
                text = ''
                for mag in battles[m.chat.id].mags.values():
                    text += '<b>{}</b>: {}♥️\n'.format(mag.name, mag.hp)
                if next_mag:
                    text += 'Следующий игрок: ' + next_mag.name
                res_text, is_end = results_to_text(res)
                bot.send_message(m.chat.id, res_text)
                if is_end:
                    battles.pop(m.chat.id)
                else:
                    bot.send_message(m.chat.id, text, parse_mode='HTML')


def results_to_text(results):
    text = ''
    for ress in results:
        if 'dead' in ress:
            text += '{} умер от {}!\n'.format(ress['dead'].name, ress['from'].name)
            continue
        if 'win' in ress:
            text += '{} победил!'.format(ress['win'].name)
            return text, True
        if 'draw' in ress:
            text += 'Ничья!'
            return text, True
        if 'heal' in ress:
            if ress['from_mag'] is ress['to_mag']:
                text += '{} выхилился на {}♥️!\n'.format(ress['from_mag'].name, ress['heal'])
            else:
                text += '{} выхилил {} на {}♥️!\n'.format(ress['from_mag'].name, ress['to_mag'].name, ress['heal'])
            continue
        if 'success' in ress and not ress['success']:
            text += 'У мага {} не получилось наколдовать свое заклинание!\n'.format(ress['mag'].name)
            continue
        damage = ress['damage']
        effects = ress['effects']
        this_text = ''
        for effect in effects:
            if 'add_cold' in effect:
                cold = effect['add_cold']
                this_text += '{} заморозил {} на {} ходов и нанес {} урона!\n'\
                    .format(cold.from_mag.name, cold.mag.name, cold.count_turns_to_end, damage)
            if 'add_term_cold' in effect:
                cold = effect['add_term_cold']
                this_text += '{} продлил заморозку {} на {} ходов и нанес {} урона!\n'\
                    .format(cold.from_mag.name, cold.mag.name, cold.power-1, damage)
            if 'end_cold' in effect:
                this_text += 'Закончилась заморозка на {}\n'.format(effect['end_cold'])
            if 'add_fire' in effect:
                fire = effect['add_fire']
                this_text += '{} поджег {} на {} ходов!\n'\
                    .format(fire.from_mag.name, fire.mag.name, fire.count_turns_to_end)
            if 'add_term_fire' in effect:
                fire = effect['add_term_fire']
                this_text += '{} продлил поджигание {} на {} ходов!\n'\
                    .format(fire.from_mag.name, fire.mag.name, fire.power-1)
            if 'end_fire' in effect:
                this_text += 'Закончился огонь на {}\n'.format(effect['end_fire'])
            if 'fire_do' in effect:
                fire = effect['fire_do']
                this_text += 'Огонь нанес {} {} урона!\n'.format(fire.mag.name, fire.power)
        if this_text == '' and damage != 0:
            this_text = '{} нанес {} урона магу {}!\n'.format(ress['from_mag'].name, damage, ress['to_mag'].name)
        text += this_text
    if text == '':
        text = 'За этот ход не произошло ничего интересного.'
    return text, False


def new_player(player_id):
    return {
        'id': player_id,
        'presets': [],
        'lvl': 1,
        'magic': {
            'types': {
                'stone': {
                    'lvl': 1,
                    'with': []
                },
                'cold': {
                    'lvl': 1,
                    'with': []
                },
                'fire': {
                    'lvl': 1,
                    'with': []
                }
            }
        }
    }


def send_menu(player_id):
    text = ''
    player = players.find_one({'id': player_id})
    text += 'Здравствуйте, {}\n'.format(player['name'])
    text += '✴️Уровень: {}\n'.format(player['lvl'])
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('🔮Пресеты'))
    bot.send_message(player_id, text, reply_markup=kb)


bot.polling(none_stop=True, timeout=600)
