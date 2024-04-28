import os
from random import randint
from dotenv import find_dotenv, load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from generator import Text2ImageAPI
from prompt_enhance import Text2TextAPI
from dblogger import Logger
from extentions import topic_check, generate_data, text_shop, enhance_history_logger


scheduler = BackgroundScheduler()
scheduler.start()
load_dotenv(find_dotenv())
BOT_KEY = os.environ.get('BOT_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
API_KEY = os.environ.get('API_KEY')
HF_KEY = os.environ.get('HF_KEY')
bot = telebot.TeleBot(BOT_KEY)
RESOLUTION = {1: (1920, 1024), 2: (1024, 1920), 3: (1536, 1024), 4: (1024, 1536), 5: (1024, 1024)}
STYLE = {1: 'DEFAULT', 2: 'ANIME', 3: 'UHD', 4: 'KANDINSKY'}
ENHANCE = {1: 'STANDART', 2: 'ENHANCE'}
resolution = style = enhance = 0


def delete_message(message, sent_message, job_id):
    scheduler.remove_job(job_id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


def generate_resolution_inline():
    markup = InlineKeyboardMarkup()

    row_1 = [InlineKeyboardButton(f'1920:1024 (16:9)', callback_data=f'option_1'),
             InlineKeyboardButton(f'1024:1920 (9:16)', callback_data=f'option_2')]
    row_2 = [InlineKeyboardButton(f'1536:1024 (3:2)', callback_data=f'option_3'),
             InlineKeyboardButton(f'1024:1536 (2:3)', callback_data=f'option_4')]
    row_3 = [InlineKeyboardButton(f'1024:1024 (1:1)', callback_data=f'option_5')]

    for row in row_1, row_2, row_3:
        markup.add(*row)
    return markup


def process_resolution_inline(call):
    resolution = int(call.data.split('_')[1])
    return RESOLUTION[resolution]


def generate_style_inline():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Стандарт', callback_data=f'style_1'))
    markup.add(InlineKeyboardButton(f'Аниме', callback_data=f'style_2'))
    markup.add(InlineKeyboardButton(f'Детальное фото', callback_data=f'style_3'))
    markup.add(InlineKeyboardButton(f'Кандинский', callback_data=f'style_4'))
    return markup


def process_style_inline(call):
    style = int(call.data.split('_')[1])
    return STYLE[style]


def generate_enhance_inline():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Стандартный', callback_data=f'enhance_1'))
    markup.add(InlineKeyboardButton(f'Тестовый', callback_data=f'enhance_2'))
    return markup


def process_enhance_inline(call):
    enhance = int(call.data.split('_')[1])
    return ENHANCE[enhance]


def get_image(call):
    message = bot.send_message(chat_id=call.message.chat.id,
                               message_thread_id=call.message.message_thread_id,
                               text=text_shop['enter_prompt'])
    return bot.register_next_step_handler(call.message, process_image, message.id)


def process_image(message, prev_msg_id):
    if not topic_check(message.message_thread_id):
        return bot.register_next_step_handler(message, process_image, prev_msg_id)
    global resolution, style, enhance
    bot.delete_message(message.chat.id, prev_msg_id)
    bot.delete_message(message.chat.id, message.id)
    loading_gif_path = f'static/{randint(1, len(os.listdir("static")))}.gif'
    with open(loading_gif_path, 'rb') as loading_gif:
        msg = bot.send_animation(chat_id=message.chat.id,
                                 message_thread_id=message.message_thread_id,
                                 animation=loading_gif)
    api_t2i = Text2ImageAPI(text_shop['url_t2i'], SECRET_KEY, API_KEY)
    base_prompt = message.text
    if enhance == 'ENHANCE':
        api_t2t = Text2TextAPI(HF_KEY, text_shop['model_t2t'])
        prompt = api_t2t.generate(base_prompt)
    else:
        prompt = base_prompt
    enhance_history_logger(base_prompt, prompt)
    result_image_path = api_t2i.get_image(prompt=prompt, width=resolution[0], height=resolution[1], style=style)
    logger = Logger()
    bot.delete_message(message.chat.id, msg.id)
    if not result_image_path:
        data = generate_data(message.from_user.id, message.from_user.username, 'timeout')
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        message_thread_id=message.message_thread_id,
                                        text=text_shop['server_issues'])
        scheduler.add_job(lambda: delete_message(message, sent_message, scheduler.get_jobs()[-1].id),
                          'interval', seconds=10)
    else:
        data = generate_data(message.from_user.id, message.from_user.username, result_image_path)
        with open(result_image_path, 'rb') as result_image:
            bot.send_photo(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                photo=result_image,
                caption=f'"{base_prompt}" по заказу @{message.from_user.username} в стиле {style} (режим {enhance})')
    logger.log(data)


@bot.message_handler(commands=['help'])
def help_command(message):
    if topic_check(message.message_thread_id):
        msg = text_shop['help']
        sent_message = bot.send_message(chat_id=message.chat.id,
                                        message_thread_id=message.message_thread_id,
                                        text=msg)
        scheduler.add_job(lambda: delete_message(message, sent_message, scheduler.get_jobs()[-1].id),
                          'interval', seconds=10)


@bot.message_handler(commands=['generate'])
def generate(message):
    if topic_check(message.message_thread_id):
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(chat_id=message.chat.id,
                         message_thread_id=message.message_thread_id,
                         text=text_shop['resolution_choose'],
                         reply_markup=generate_resolution_inline())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global resolution, style, enhance
    if call.data.startswith('option_'):
        bot.delete_message(call.message.chat.id, call.message.id)
        resolution = process_resolution_inline(call)
        bot.send_message(chat_id=call.message.chat.id,
                         message_thread_id=call.message.message_thread_id,
                         text=text_shop['style_choose'],
                         reply_markup=generate_style_inline())
    elif call.data.startswith('style_'):
        bot.delete_message(call.message.chat.id, call.message.id)
        style = process_style_inline(call)
        bot.send_message(chat_id=call.message.chat.id,
                         message_thread_id=call.message.message_thread_id,
                         text=text_shop['enhance_choose'],
                         reply_markup=generate_enhance_inline())
    elif call.data.startswith('enhance_'):
        bot.delete_message(call.message.chat.id, call.message.id)
        enhance = process_enhance_inline(call)
        get_image(call)


if __name__ == '__main__':
    bot.infinity_polling()
