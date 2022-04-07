from typing import Dict, List, Union

from aio_yandex_tracker import types
from yarl import URL


class HttpResponse:
    body: Union[Dict, List, int]

    def __init__(
        self,
        status: int,
        reason: str,
        url: URL,
        headers: types.HEADERS_OBJECT,
        body: Union[Dict, List, int],
    ):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.url = url
        self.body = body
