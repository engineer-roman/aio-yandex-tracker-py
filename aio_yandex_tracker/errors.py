from http import HTTPStatus
from typing import Any


class ApiUnknownError(BaseException):
    pass


class HTTPError(BaseException):
    def __init__(
        self, message: str, status_code: int, reason: str, response_body: Any
    ):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
        self.response_body = response_body


class AuthRequiredError(HTTPError):
    pass


class NotFoundError(HTTPError):
    pass


class ApiUnavailableError(HTTPError):
    pass


class ApiBadRequestError(HTTPError):
    pass


class IncorrectDataError(HTTPError):
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
