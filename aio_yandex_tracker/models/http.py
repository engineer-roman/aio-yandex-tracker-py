from typing import Dict

from aio_yandex_tracker import types


class HttpResponse:
    def __init__(
        self,
        status: int,
        reason: str,
        url: str,
        headers: types.HEADERS_OBJECT,
        body: Dict,
    ):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.url = url
        self.body = body
