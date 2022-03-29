from typing import Callable, Tuple

from aio_yandex_tracker import const, types
from aio_yandex_tracker.session import HttpSession
from pytest import fixture


@fixture
def base_session() -> Callable:
    session_preset = {
        "token": "Test Token",
        "org_id": 12345,
    }

    def get_session(loop=None):
        return HttpSession(**session_preset, loop=loop)

    return get_session


@fixture
def customized_session() -> Tuple[Callable, types.SESSION_PRESET]:
    session_preset = {
        "token": "Test Token",
        "org_id": 12345,
        "api_root": (
            f"localhost.localdomain:{const.TEST_AIOHTTP_SERVER_PORT}"
        ),
        "api_version": "3",
        "api_schema": "http",
        "headers": {"X-Custom-Header": "custom_value"},
    }

    def get_session(loop=None):
        return HttpSession(**session_preset, loop=loop)

    return get_session, session_preset
