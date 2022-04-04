from enum import Enum
from http import HTTPStatus


class API_VERSION_NAME(Enum):
    V1 = "v1"
    V2 = "v2"


API_HEADERS_DEFAULT = {"Content-type": "application/json"}
API_URL_SCHEMA = "https"
API_URL_ROOT = "api.tracker.yandex.net"

API_ISSUES_URL = "/issues"
API_ISSUES_DIRECT_URL = f"{API_ISSUES_URL}/{{id}}"
API_ISSUES_MOVE_URL = f"{API_ISSUES_URL}/{{id}}/_move"
API_ISSUES_COUNT_URL = f"{API_ISSUES_URL}/_count"
API_ISSUES_SEARCH_URL = f"{API_ISSUES_URL}/_search"

HTTP_METHODS = ["get", "patch", "post", "put", "delete"]
RESPONSE_ENCODING_DEFAULT = "utf-8"
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


# Tests
TEST_AIOHTTP_SERVER_PORT = 20001
TEST_TRACKER_TOKEN = "Test token"
TEST_TRACKER_ORG_ID = 12345
