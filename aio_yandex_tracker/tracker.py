from asyncio import AbstractEventLoop
from types import TracebackType
from typing import Any, Dict, Optional, Type, Union

from aio_yandex_tracker import const, types
from aio_yandex_tracker.models import api as api_models
from aio_yandex_tracker.models.http import HttpResponse
from aio_yandex_tracker.session import HttpSession
from aio_yandex_tracker.types import HEADERS_OBJECT


class YandexTracker:
    def __init__(
        self,
        token: str,
        org_id: Union[int, str],
        api_root: Optional[str] = None,
        api_version: Optional[str] = None,
        api_schema: Optional[str] = None,
        headers: Optional[HEADERS_OBJECT] = None,
        response_encoding: str = const.RESPONSE_ENCODING_DEFAULT,
        loop: Optional[AbstractEventLoop] = None,
        retries: Optional[int] = const.BACKOFF_RETRIES,
        retry_interval: Optional[int] = const.BACKOFF_RETRY_INTERVAL,
    ):
        self.__session = HttpSession(
            token=token,
            org_id=org_id,
            api_root=api_root,
            api_version=api_version,
            api_schema=api_schema,
            headers=headers,
            response_encoding=response_encoding,
            loop=loop,
            retries=retries,
            retry_interval=retry_interval,
        )
        self.__issues = api_models.Issues(self.__session)
        self.__priorities = api_models.Priorities(self.__session)

    @property
    def issues(self):
        return self.__issues

    @property
    def priorities(self):
        return self.__priorities

    async def raw_query(
        self,
        url: str,
        method: str,
        params: Optional[types.PARAMS_OBJECT] = None,
        headers: Optional[types.HEADERS_OBJECT] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> HttpResponse:
        opts = {
            "url": url,
            "method": method,
            "params": params or {},
            "headers": headers or {},
        }
        if payload:
            opts["json"] = payload
        return await self.__session.request(**opts)

    @property
    def is_closed(self) -> bool:
        return self.__session.is_closed

    async def close(self) -> None:
        await self.__session.close()

    async def __aenter__(self) -> "YandexTracker":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()
