from typing import Optional, Union

from aio_yandex_tracker import const
from aio_yandex_tracker.types import HEADERS_OBJECT
from aiohttp import ClientSession


class HttpSession:
    def __init__(
        self,
        token: str,
        org_id: Union[int, str],
        api_root: Optional[str] = None,
        api_version: Optional[str] = None,
        headers: Optional[HEADERS_OBJECT] = None,
    ):
        api_root = api_root or const.API_URL_ROOT
        api_version = api_version or const.API_VERSION_NAME.V2.value
        self.base_url = f"{api_root}/{api_version}/"
        user_headers = headers or {}
        self.headers = {
            **const.API_HEADERS_DEFAULT,
            **user_headers,
            "Host": self.base_url,
            "Authorization": f"OAuth {token}",
            "X-Org-ID": str(org_id),
        }
        self.__session: Optional[ClientSession] = ClientSession(
            headers=self.headers
        )

    # async def request(self, method: str, url: str, *args, **kwargs):
    #
    #     pass
    #
    # async def __send_request(self, method: str, url: str, *args, **kwargs):
    #     if not self.is_active:
    #         raise errors.SessionIsNotInitialized
    #     return await self.__session

    @property
    def is_active(self):
        return True if self.__session and not self.__session.closed else False

    def close(self):
        if not self.__session._loop.is_closed():
            self.__session._loop.run_until_complete(self.__session.close())
            self.__session = None
            return True
        return False

    def __del__(self):
        if self.is_active:
            self.close()
