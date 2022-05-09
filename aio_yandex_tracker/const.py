from enum import Enum
from http import HTTPStatus


class API_VERSION_NAME(Enum):
    V1 = "v1"
    V2 = "v2"


API_HEADERS_DEFAULT = {"Content-type": "application/json"}
API_URL_SCHEMA = "https"
API_URL_ROOT = "api.tracker.yandex.net"

# API URLs
ISSUES_URL = "issues"
ISSUES_COUNT_URL = f"{ISSUES_URL}/_count"
ISSUES_SEARCH_URL = f"{ISSUES_URL}/_search"
ISSUES_DIRECT_URL = f"{ISSUES_URL}/{{id}}"
ISSUES_MOVE_URL = f"{ISSUES_DIRECT_URL}/_move"
CHANGELOG_URL = f"{ISSUES_DIRECT_URL}/changelog"
LINKS_URL = f"{ISSUES_DIRECT_URL}/links"
TRANSITIONS_URL = f"{ISSUES_DIRECT_URL}/transitions"
TRANSITIONS_EXEC_URL = f"{TRANSITIONS_URL}/{{transition_id}}/_execute"

PRIORITIES_URL = "priorities"


# ---
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
    HTTPStatus.TOO_MANY_REQUESTS,
)
BACKOFF_RETRIES = 0
BACKOFF_RETRY_INTERVAL = 1


# Tests
TEST_AIOHTTP_SERVER_PORT = 20001
TEST_TRACKER_TOKEN = "Test token"
TEST_TRACKER_ORG_ID = 12345
