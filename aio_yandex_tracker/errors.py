class ApiUnknownError(BaseException):
    pass


class HTTPError(BaseException):
    pass


class ApiError(HTTPError):
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
