### Practicum_bot

```
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Задеплоен на https://www.pythonanywhere.com/
Присылает сообщения при изменении статуса проверки дз - "Проверка", "Есть замечания", "Зачтено".
```

### Стэк технологий:
- Python 3.11
- python-dotenv 0.20.0
- python-telegram-bot 13.7

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/Forget-me-not-crossyroad/homework_bot
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env (для Linux "python3 -m venv env")
```

```
source env/Scripts/activate (для Linux "source env/bin/activate")
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip (для Linux "python3 -m pip install --upgrade pip")
```

```
pip install -r requirements.txt
```

Записать в переменные окружения (файл .env) необходимые ключи:
- токен профиля студента на Яндекс Практикум
- токен для телеграм-бота
- свой ID в телеграме

Выполнить миграции:

```
python manage.py migrate (для Linux "python3 manage.py migrate")
```

Запустить проект:

```
python manage.py runserver (для Linux "python3 manage.py runserver")
```
