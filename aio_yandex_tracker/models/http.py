from typing import Dict, Union

from aio_yandex_tracker import types


class HttpResponse:
    body: dict

    def __init__(
        self,
        status: int,
        reason: str,
        url: str,
        headers: types.HEADERS_OBJECT,
        body: Union[Dict, int],
    ):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.url = url
        self.body = body
