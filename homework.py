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
    return (
        os.getenv('PRACTITCUM_TOKEN')
        and os.getenv('TELEGRAM_TOKEN')
        and os.getenv('TELEGRAM_CHAT_ID')
    )


def send_message(bot, message):
    """Отправка ботом сообщения в чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(timestamp):
    """Отправка запроса к API Practicum."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    return response.json()


def check_response(response):
    """Проверка соответствия ответа от сервера документации."""
    return (
        type(response['homeworks']) == list
        and type(response['current_date']) == int
    )


def parse_status(homework):
    """Получение информации о статусе и названии конкретной домашней работы."""
    homework_name, verdict = homework['homework_name'], homework['status']
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    # response = get_api_answer(timestamp)
    # check_response(response)
    # homework_status = response['homework'][-1].get('status')

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            parse_status(response['homework'][-1])
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            # ...
        send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
