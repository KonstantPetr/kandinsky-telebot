from datetime import datetime
from random import uniform


TOPIC_NAMES = [3, 10333]

text_shop = {
    'enter_prompt': 'Введите промпт',
    'url_t2i': 'https://api-key.fusionbrain.ai/',
    'server_issues': 'Сервер приболел, попробуйте ещё раз через некоторое время...',
    'help': 'Чтобы сгенерировать картиночку нажмите /generate и следуйте инструкциям.\n'
            'На текущий момент покдлючено API с цензурой, поэтому на "нехорошие" запросы выдаёт ромашку.\n'
            'Добавлена тестовая функция для улучшения результатов, превращающая бота в ансамбль нейросетей.\n'
            'Тестовый режим используйте на свой страх и риск, результаты могут быть непредсказуемы!',
    'resolution_choose': 'Выберите соотношение сторон',
    'style_choose': 'Выберите стиль',
    'enhance_choose': 'Выберите режим',
    'model_t2t': 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO',
    'prompt_helper_t2t': [
        'улучши промпт для нейросети, которая будет генерировать по нему изображение: ',
        ' Напиши улучшенный вариант, чтобы нейросеть хорошо его обработала и представила \
наилучший результат. Напиши просто сам промпт БЕЗ пояснений БЕЗ дополнительной информации. Напиши на русском языке. \
Ответь обязательно в следующем формате - Промпт: текст промпта :конец.'
    ]
}


def topic_check(topic_name):
    return topic_name in TOPIC_NAMES


def generate_data(user_id, user_name, image_path):
    current_dtm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return user_id, user_name, image_path, current_dtm


def random_temperature():
    min_value = 0.50
    max_value = 0.80
    step = 0.01
    return round(uniform(min_value, max_value + step), 2)


def enhance_history_logger(base_prompt, prompt):
    content = ''
    try:
        with open('logs/enhance_log.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        pass
    content += f'\n\n{base_prompt}\n{prompt}'
    with open('logs/enhance_log.txt', 'w', encoding='utf-8') as f:
        f.write(content.strip('\n'))
