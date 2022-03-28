from typing import Tuple

from aio_yandex_tracker import types
from aio_yandex_tracker.session import HttpSession
from pytest import fixture


@fixture
def base_session() -> HttpSession:
    return HttpSession("Test Token", 12345)


@fixture
def customized_session() -> Tuple[types.SESSION_PRESET, HttpSession]:
    session_preset = {
        "token": "Test Token",
        "org_id": 12345,
        "api_root": "http://localhost.localdomain",
        "api_version": "123",
        "headers": {"X-Custom-Header": "custom_value"},
    }
    return session_preset, HttpSession(**session_preset)
