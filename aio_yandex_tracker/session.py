from asyncio import AbstractEventLoop
from typing import Dict, Optional, Union

from aio_yandex_tracker import const, errors, types
from aio_yandex_tracker.models.http import HttpResponse
from aio_yandex_tracker.types import HEADERS_OBJECT
from aiohttp import ClientResponse, ClientSession


class HttpSession:
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
        api_root = api_root or const.API_URL_ROOT
        api_schema = api_schema or const.API_URL_SCHEMA
        self.api_version = api_version or const.API_VERSION_NAME.V2.value
        self.base_url = f"{api_schema}://{api_root}"
        self._api_url = "{base}/{version}/{endpoint}"
        user_headers = headers or {}
        self.headers = {
            **const.API_HEADERS_DEFAULT,
            **user_headers,
            "Host": api_root.split("/")[0],
            "Authorization": f"OAuth {token}",
            "X-Org-ID": str(org_id),
        }
        self.response_encoding = response_encoding
        self.__session: Optional[ClientSession] = ClientSession(
            headers=self.headers, loop=loop
        )

    async def fetch(self, endpoint, method, *args, **kwargs):
        return await self.request(
            self._api_url.format(
                base=self.base_url, version=self.api_version, endpoint=endpoint
            ),
            method,
            *args,
            **kwargs,
        )

    async def request(
        self, url: str, method: str, *args, **kwargs
    ) -> HttpResponse:
        retry = 0
        retry_limit = 0
        response = await self.__send_request(
            url,
            method,
            *args,
            **kwargs,
        )
        # FIXME add backoff settings
        while retry < retry_limit and self.retry_needed(response):
            response = await self.__send_request(
                url,
                method,
                *args,
                **kwargs,
            )
            if not self.retry_needed(response):
                break
            retry += 1

        await self.validate_http_response(response, self.response_encoding)
        return HttpResponse(
            response.status,
            response.reason,
            response.url,
            response.headers,
            await response.json(encoding=self.response_encoding),
        )

    async def __send_request(
        self, endpoint: str, method: str, *args, **kwargs
    ) -> ClientResponse:
        if not self.is_closed:
            raise errors.SessionNotInitializedError(
                "Instance session is not active. Re-create instance"
            )
        http_method = self.validate_http_method(self.__session, method)
        try:
            return await http_method(endpoint, *args, **kwargs)
        except Exception as exc:
            raise errors.ApiUnknownError(f"{exc.__class__.__name__} - {exc}")

    @staticmethod
    def retry_needed(response: ClientResponse) -> bool:
        if response.status in const.RESPONSE_CODES_RETRY:
            return True
        return False

    @staticmethod
    async def validate_http_response(
        response: ClientResponse, encoding=const.RESPONSE_ENCODING_DEFAULT
    ) -> None:
        if response.status in const.RESPONSE_CODES_OK:
            return

        try:
            error_body = await response.json(encoding=encoding)
        except Exception:
            # FIXME log exception
            error_body = None

        # if error_body:
        #     # FIXME add logging
        #     pass
        exc_class = errors.HTTP_ERRORS_MAPPING.get(
            response.status, errors.ApiUnavailableError
        )(
            f"Request failed: {response.status} - {response.reason}",
            response.status,
            response.reason,
            response.url.human_repr(),
            error_body,
            response.headers,
        )
        raise exc_class

    @staticmethod
    def validate_http_method(session, method):
        if method in const.HTTP_METHODS:
            result = getattr(session, method, None)
            if result:
                return result
        raise errors.UnknownHttpMethodError(
            f"Unknown method for HTTP Session: {method}"
        )

    @staticmethod
    def serialize_headers_links(
        headers: types.HEADERS_OBJECT,
    ) -> Dict[str, str]:
        links = {}
        for header, value in headers.items():
            if header == "Link":
                link, link_type = value.split("; rel=")
                links[link_type.strip('""')] = link.strip("<>")
        return links

    @property
    def is_closed(self):
        return (
            True if not self.__session or not self.__session.closed else False
        )

    async def close(self):
        if self.is_closed:
            await self.__session.close()
            self.__session = None
            return True
        return False
