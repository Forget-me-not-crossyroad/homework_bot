import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from expections import ApiGetRequestError

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='a',
)

formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

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

TOKEN_NAMES = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')


def check_tokens():
    """Проверка наличия необходимых для работы бота переменных окружения."""
    for name in TOKEN_NAMES:  # Все-таки получилось
        if not globals()[name]:
            raise KeyError(
                logging.critical(
                    f'Отсутствует переменная окружения {name}', exc_info=True
                )
            )


def send_message(bot, message):
    """Отправка ботом сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError as error:
        logging.error(
            f'Ошибка при попытке отправить сообщение: {error}', exc_info=True
        )
    logging.debug(
        'Сообщение о статусе домашней работы отправлено в телеграм-чат'
    )


def get_api_answer(timestamp):
    """Отправка запроса к API Practicum."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        raise ConnectionError(
            logging.error(
                f'Ошибка при запросе' f'к основному API: {error}',
                exc_info=True,
            )
        )
    if response.status_code != HTTPStatus.OK:
        raise ApiGetRequestError(
            logging.error(
                f'Запрос не был выполнен. Код ответа {response.status_code}',
                exc_info=True,
            )
        )
    return response.json()


def check_response(response):
    """Проверка соответствия ответа от сервера документации."""
    if not isinstance(response, dict):
        raise TypeError(
            logging.error(
                'Возвращаемый ответ имеет тип данных, отличный от dict',
                exc_info=True,
            )
        )
    if response.get('homeworks') is None:
        raise KeyError(
            logging.error(
                'Отсутствует ключ "homeworks"',
                exc_info=True,
            )
        )
    if isinstance(response['homeworks'], list) is not True:
        raise TypeError(
            logging.error(
                'Получен некорректный ответ от сервера.'
                'Тип ключа "homework" или "current_date"'
                'не соответствует документации',
                exc_info=True,
            )
        )


def parse_status(homework):
    """Получение информации о статусе и названии конкретной домашней работы."""
    status = homework['status']
    try:
        verdict = HOMEWORK_VERDICTS[status]
        homework_name = homework['homework_name']
    except KeyError as error:
        logging.error(
            f'В полученном ответе от сервера'
            f'отсутствует необходимый ключ "{error}"',
            exc_info=True,
        )
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
            else:
                logging.debug('В ответе от сервера отсутствуют новые статусы')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Ошибка в работе программы: {error}', exc_info=True)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
