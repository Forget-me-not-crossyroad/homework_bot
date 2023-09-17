from http import HTTPStatus


class BaseError(Exception):
    """Базовый класс кастомных Exceptions."""

    def __init__(
        self,
        msg="Запрос не был выполнен",
        code=HTTPStatus.BAD_REQUEST,
    ):
        """Конструктор класса BaseError.
        Передаются сообщение и код ответа сервера
        """
        self.msg = msg
        self.code = code


class ApiGetRequestError(BaseError):
    """Ошибка отправки сообщения пользователю."""

    pass
