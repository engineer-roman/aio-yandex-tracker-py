from enum import Enum

API_HEADERS_DEFAULT = {"Content-type": "application/json"}
API_URL_ROOT = "https://api.tracker.yandex.net"

HTTP_METHODS = ["get", "post", "put", "delete"]
RESPONSE_CODES_OK = (200, 201, 204)
RESPONSE_CODES_RETRY = (500, 502, 503, 504)


class API_VERSION_NAME(Enum):
    V1 = "v1"
    V2 = "v2"
