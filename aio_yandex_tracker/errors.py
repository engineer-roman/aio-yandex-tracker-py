from http import HTTPStatus
from typing import Any, Optional

from aio_yandex_tracker import types


class ApiUnknownError(BaseException):
    pass


class HttpError(BaseException):
    def __init__(
        self,
        message: str,
        status_code: int,
        reason: str,
        url: str,
        response_body: Any,
        headers: Optional[types.HEADERS_OBJECT] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
        self.headers = headers
        self.response_body = response_body
        self.url = url


class AuthRequiredError(HttpError):
    pass


class NotFoundError(HttpError):
    pass


class ApiUnavailableError(HttpError):
    pass


class ApiBadRequestError(HttpError):
    pass


class IncorrectDataError(HttpError):
    pass


class SessionIsNotInitialized(BaseException):
    pass


class UnknownHttpMethod(BaseException):
    pass


HTTP_ERRORS_MAPPING = {
    HTTPStatus.BAD_REQUEST: ApiBadRequestError,
    HTTPStatus.UNPROCESSABLE_ENTITY: IncorrectDataError,
    HTTPStatus.UNAUTHORIZED: AuthRequiredError,
    HTTPStatus.FORBIDDEN: AuthRequiredError,
    HTTPStatus.NOT_FOUND: NotFoundError,
}
