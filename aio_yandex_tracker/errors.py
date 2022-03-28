class ApiUnknownError(BaseException):
    pass


class ApiRawError(BaseException):
    pass


class ApiUnavailableError(BaseException):
    pass


class ApiBadRequestError(BaseException):
    pass


class IncorrectDataError(BaseException):
    pass


class SessionIsNotInitialized(BaseException):
    pass
