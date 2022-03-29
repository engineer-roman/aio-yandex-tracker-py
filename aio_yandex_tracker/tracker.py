from asyncio import AbstractEventLoop
from types import TracebackType
from typing import Optional, Type, Union

from aio_yandex_tracker import const
from aio_yandex_tracker.session import HttpSession
from aio_yandex_tracker.types import HEADERS_OBJECT

# from aio_yandex_tracker.models.tracker import Issues


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
    ):
        self.__session = HttpSession(
            token,
            org_id,
            api_root,
            api_version,
            api_schema,
            headers,
            response_encoding,
            loop,
        )
        # self.__issues = Issues(self.__session)

    # @property
    # def issues(self):
    #     return self.__issues

    @property
    def is_closed(self):
        return self.__session.is_closed

    async def close(self):
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
