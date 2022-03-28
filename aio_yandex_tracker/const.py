from enum import Enum
from http import HTTPStatus

API_HEADERS_DEFAULT = {"Content-type": "application/json"}
API_URL_ROOT = "https://api.tracker.yandex.net"

HTTP_METHODS = ["get", "post", "put", "delete"]
RESPONSE_CODES_OK = (
    HTTPStatus.OK,
    HTTPStatus.CREATED,
    HTTPStatus.NO_CONTENT,
)
RESPONSE_CODES_RETRY = (
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
)


class API_VERSION_NAME(Enum):
    V1 = "v1"
    V2 = "v2"
