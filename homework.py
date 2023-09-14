import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from expections import ApiGetRequestError, SendMessageError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)

logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
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


TOKENS_LIST = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']


def check_tokens():
    """Проверка наличия необходимых для работы бота переменных окружения."""
    if PRACTICUM_TOKEN is None or PRACTICUM_TOKEN == '':
        logging.critical(
            'Отсутствует или пуста переменная окружения PRACTICUM_TOKEN'
        )
        sys.exit(1)
    if TELEGRAM_TOKEN is None or TELEGRAM_TOKEN == '':
        logging.critical('Отсутствует переменная окружения TELEGRAM_TOKEN')
        sys.exit(1)
    if TELEGRAM_CHAT_ID is None or TELEGRAM_CHAT_ID == '':
        logging.critical('Отсутствует переменная окружения TELEGRAM_CHAT_ID')
        sys.exit(1)
    else:
        pass


def send_message(bot, message):
    """Отправка ботом сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except SendMessageError as error:
        logging.error(f'Ошибка при попытке отправить сообщение: {error}')
    logging.debug(
        'Сообщение о статусе домашней работы отправлено в телеграм-чат'
    )


def get_api_answer(timestamp):
    """Отправка запроса к API Practicum."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        raise ApiGetRequestError(
            f'Запрос не был выполнен. Код ответа {response.status_code}'
        )
    return response.json()


def check_response(response):
    """Проверка соответствия ответа от сервера документации."""
    if isinstance(response, dict) is not True:
        raise TypeError(
            logging.error(
                'Возвращаемый ответ имеет тип данных, отличный от dict'
            )
        )
    if response.get('homeworks') is None:
        raise KeyError(logging.error('Отсутствует ключ'))
    if isinstance(response['homeworks'], list) is not True:
        raise TypeError(
            'Получен некорректный ответ от сервера.'
            'Тип ключа "homework" или "current_date"'
            'не соответствует документации'
        )


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

    message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            updated_message = parse_status(response['homeworks'][0])
            if updated_message != message:
                send_message(bot, updated_message)
                message = updated_message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Ошибка в работе программы: {error}')

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
