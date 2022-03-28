from typing import Optional, Union

from aio_yandex_tracker import const, errors
from aio_yandex_tracker.types import HEADERS_OBJECT
from aiohttp import ClientResponse, ClientSession


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

    async def request(
        self, method: str, url: str, *args, **kwargs
    ) -> ClientResponse:
        retry = 0
        retry_limit = 0
        response = await self.__send_request(method, url, *args, **kwargs)
        while retry < retry_limit and self.retry_needed(response):
            response = await self.__send_request(method, url, *args, **kwargs)
            if not self.retry_needed(response):
                break
            retry += 1
            # FIXME add logging

        await self.validate_http_response(response)
        return response

    async def __send_request(
        self, method: str, url: str, *args, **kwargs
    ) -> ClientResponse:
        if not self.is_active:
            raise errors.SessionIsNotInitialized(
                "Instance session is not active. Re-create instance"
            )
        http_method = self.validate_http_method(self.__session, method)
        try:
            return await http_method(url, *args, **kwargs)
        except Exception as exc:
            raise errors.ApiUnknownError(f"{exc.__class__.__name__} - {exc}")

    @staticmethod
    def retry_needed(response: ClientResponse) -> bool:
        if response.status in const.RESPONSE_CODES_RETRY:
            return True
        return False

    @staticmethod
    async def validate_http_response(
        response: ClientResponse, encoding="utf-8"
    ) -> None:
        if response.status in const.RESPONSE_CODES_OK:
            return

        try:
            error_body = await response.json(encoding=encoding)
        except Exception:
            # FIXME log exception
            error_body = None

        exc_class = errors.HTTP_ERRORS_MAPPING.get(
            response.status, errors.ApiUnavailableError
        )(
            f"API Error received for URL {response.url}",
            response.status,
            response.reason,
            error_body,
        )
        raise exc_class

    @staticmethod
    def validate_http_method(session, method):
        if method in const.HTTP_METHODS:
            result = getattr(session, method, None)
            if result:
                return result
        raise errors.UnknownHttpMethod(
            f"Unknown method for HTTP Session: {method}"
        )

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