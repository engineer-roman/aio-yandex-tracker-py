from typing import Dict


class HTTPResponse:
    def __init__(self, status: int, reason: str, url: str, body: Dict):
        self.status = status
        self.reason = reason
        self.url = url
        self.body = body
