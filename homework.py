from http import HTTPStatus
import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)

logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRACTITCUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Проверка наличия необходимых для работы бота переменных окружения."""
    try:
        (
            os.getenv('PRACTITCUM_TOKEN')
            and os.getenv('TELEGRAM_TOKEN')
            and os.getenv('TELEGRAM_CHAT_ID')
        )
    except Exception as error:
        logging.error(f'Ошибка при попытке отправить сообщение: {error}')


def send_message(bot, message):
    """Отправка ботом сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка при попытке отправить сообщение: {error}')
    logging.debug('123')


def get_api_answer(timestamp):
    """Отправка запроса к API Practicum."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Запрос не был выполнен. Код ответа {response.status_code}')
    return response.json()


def check_response1(response):
    """Проверка соответствия ответа от сервера документации."""
    if isinstance(response, dict) is not True:
        raise TypeError(logging.error('Возвращаемый ответ имеет тип данных, отличный от dict'))
    try:
        value_hw = response['homeworks']
    except KeyError as error:
        logging.error(f'Отсутствует ключ: {error}')
    if isinstance(value_hw, list) is not True:
        raise TypeError('Получен некорректный ответ от сервера.'
                        'Тип ключа "homework" или "current_date"'
                        'не соответствует документации')
    

def check_response(response):
    """Проверка соответствия ответа от сервера документации."""
    if isinstance(response, dict) is not True:
        raise TypeError(logging.error('Возвращаемый ответ имеет тип данных, отличный от dict'))
    if response.get('homeworks') is None:
        raise KeyError(logging.error('Отсутствует ключ'))        
    if isinstance(response['homeworks'], list) is not True:
        raise TypeError('Получен некорректный ответ от сервера.'
                        'Тип ключа "homework" или "current_date"'
                        'не соответствует документации')
    

def check_response2(response):
    """Проверка соответствия ответа от сервера документации."""
    try:
        isinstance(response, dict) is True
        response.get('homeworks') is not None
        isinstance(response['homeworks'], list) is True
    except TypeError as error:
        logging.error(f'{error} Возвращаемый ответ имеет тип данных, отличный от dict')
    except KeyError as error:
        logging.error(f'{error} Получен некорректный ответ от сервера.'
                      'Тип ключа "homework" или "current_date"'
                      'не соответствует документации')


# def parse_status1(homework):
#     """Получение информации о статусе и названии конкретной домашней работы."""
#     try:
#         if homework[-1]['status'] in HOMEWORK_VERDICTS:
#             homework_name, verdict = homework[-1]['homework_name'], HOMEWORK_VERDICTS[homework[-1]['status']]
#     except Exception as error:
#         logging.error(f'Ошибка при запросе к основному API: {error}')
#     return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def parse_status(homework):
    """Получение информации о статусе и названии конкретной домашней работы."""
    status = homework['status']
    try:
        verdict = HOMEWORK_VERDICTS[status]
        homework_name = homework['homework_name']
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            parse_status(response['homework'][-1])
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Ошибка в работе программы: {error}')
        send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
