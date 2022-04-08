import uuid
from typing import Any, Dict, Optional, Type, Union

from aio_yandex_tracker import const, errors
from aio_yandex_tracker.models.http import HttpResponse
from aio_yandex_tracker.session import HttpSession


class BaseEntity:
    __original_payload = None
    # {field_name: (is_required, alias_name)}
    _fields = {}

    def __init__(self, payload: Dict[str, Any], session: HttpSession):
        self._session = session
        self.original_payload = payload

    @property
    def original_payload(self) -> Dict[str, Any]:
        return self.__original_payload

    @original_payload.setter
    def original_payload(self, value: Dict[str, Any]) -> None:
        self.set_fields(value)
        self.__original_payload = value

    def set_fields(self, payload: Dict[str, Any]) -> None:
        for name, meta in self._fields.items():
            required, alias = meta
            alias = alias or name
            if alias.startswith("__") or alias == "original_payload":
                continue

            try:
                value = payload[name]
                setattr(self, alias, value)
            except KeyError:
                if not required:
                    continue
                raise errors.FieldMissingError(
                    f"Required field for {self.__class__.__name__} "
                    f"is missing: {name}"
                )

    def as_dict(self, original_names: bool = False) -> Dict[str, Any]:
        output = {}
        for name, meta in self.__fields.items():
            attr_name = meta[1] or name
            field_name = name if original_names else attr_name
            try:
                value = getattr(self, attr_name)
            except AttributeError:
                continue
            output[field_name] = value

        return output


class Collection(list):
    def __init__(
        self,
        response: HttpResponse,
        session: HttpSession,
        entity_cls: Type[BaseEntity],
        method: str,
        parent_id: Optional[str] = None,
        payload: Optional[Dict] = None,
    ):
        parent_id_dict = {"__parent_id": parent_id} if parent_id else {}
        super(Collection, self).__init__(
            [
                entity_cls({**x, **parent_id_dict}, session)
                for x in response.body
            ]
        )
        self.__session = session
        self._entity_cls = entity_cls
        self._parent_id = parent_id
        self._url = response.url
        self._endpoint = response.url.human_repr()[
            len(session.base_url) :  # noqa E203
        ]
        self._page = int(self._url.query.get("page", "1"))
        self._total_pages = int(response.headers.get("X-Total-Pages", 0))
        self._total_entities = int(response.headers.get("X-Total-Count", 0))
        self._request_method = method
        self._request_payload = payload or {}

    @property
    def page(self) -> int:
        return self._page

    @property
    def total_pages(self) -> int:
        return self._total_pages

    @property
    def total_entities(self) -> int:
        return self._total_entities

    async def turn_page(self, page: int):
        if page < 1 or page > self._total_pages or page == self._page:
            raise errors.PaginationProhibitedError(
                f"Cannot turn page to {page}"
            )
        page = page or (self._page + 1)
        if self.page >= self.total_pages:
            raise errors.PaginationProhibitedError("No next page found")
        response = await self.__session.request(
            self._request_method,
            self._endpoint,
            params={**self._url.query, "page": page},
            json=self._request_payload,
        )
        return self.__class__(
            response,
            self.__session,
            self._entity_cls,
            self._request_method,
            self._request_payload,
        )

    async def load_next(self):
        return await self.turn_page(self._page + 1)

    async def load_prev(self):
        return await self.turn_page(self._page - 1)


class Priority:
    pass


class Transition(BaseEntity):
    _fields = {
        "self": (True, "self_url"),
        "id": (True, None),
        "display": (True, None),
        "to": (False, None),
    }
    __parent_id = None
    id = None

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.id}>"

    def __str__(self):
        return self.id

    async def apply(
        self, payload: Optional[Dict] = None, comment: Optional[str] = None
    ) -> Collection:
        endpoint = const.TRANSITIONS_EXEC_URL.format(
            id=self.__parent_id, transition_id=self.id
        )
        payload = payload or {}
        if comment:
            payload["comment"] = comment

        response = await self._session.request("post", endpoint, payload)
        return Collection(
            response,
            self._session,
            Transition,
            "post",
            self.__parent_id,
            payload,
        )


class Issue(BaseEntity):
    _fields = {
        "self": (True, "self_url"),
        "id": (True, None),
        "key": (True, None),
        "aliases": (False, None),
        "assignee": (False, None),
        "createdAt": (False, "created_at"),
        "createdBy": (False, "created_by"),
        "description": (False, None),
        "favorite": (False, None),
        "followers": (False, None),
        "lastCommentUpdatedAt": (False, "last_comment_updated_at"),
        "parent": (False, None),
        "previousStatus": (False, "previous_status"),
        "priority": (False, None),
        "queue": (False, None),
        "resolution": (False, None),
        "sprint": (False, None),
        "status": (False, None),
        "statusStartTime": (False, "status_start_time"),
        "start": (False, None),
        "summary": (False, None),
        "tags": (False, None),
        "type": (False, None),
        "unique": (False, None),
        "updatedAt": (False, "updated_at"),
        "updatedBy": (False, "updated_by"),
        "version": (False, None),
        "votes": (False, None),
    }
    key = None

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.key}>"

    def __str__(self):
        return self.key

    async def reload(self) -> Union["Issue", bool]:
        if not self.key:
            return False
        data = await self._session.request(
            "get", const.ISSUES_DIRECT_URL.format(id=self.key)
        )
        self.original_payload = data.body

    async def transitions(self) -> Collection:
        endpoint = const.TRANSITIONS_URL.format(id=self.key)
        response = await self._session.request("get", endpoint)
        return Collection(response, self._session, Transition, "get", self.key)

    async def apply_transition(
        self,
        transition_id: str,
        payload: Optional[Dict] = None,
        comment: Optional[str] = None,
    ) -> Collection:
        endpoint = const.TRANSITIONS_EXEC_URL.format(
            id=self.key, transition_id=transition_id
        )
        payload = payload or {}
        if comment:
            payload["comment"] = comment

        response = await self._session.request("post", endpoint, json=payload)
        return Collection(
            response, self._session, Transition, "post", self.key, payload
        )


class Issues:
    __single_entity_cls = Issue

    def __init__(self, session: HttpSession):
        self.__session = session

    def model_response(self, response: HttpResponse) -> Union[BaseEntity, int]:
        if isinstance(response.body, dict):
            return self.__single_entity_cls(response.body, self.__session)
        elif isinstance(response.body, list):
            return 0
        return response.body

    async def get(
        self, entity_id: str, params: Optional[Dict] = None
    ) -> Issue:
        endpoint = const.ISSUES_DIRECT_URL.format(id=entity_id)
        response = await self.__session.request(
            "get", endpoint, params=params or {}
        )
        return Issue(response.body, self.__session)

    async def transitions(self, entity_id: str) -> Collection:
        endpoint = const.TRANSITIONS_URL.format(id=entity_id)
        response = await self.__session.request("get", endpoint)
        return Collection(
            response, self.__session, Transition, "get", entity_id
        )

    async def create(self, payload: Dict[str, Any]) -> Issue:
        endpoint = const.ISSUES_URL
        payload.setdefault("unique", uuid.uuid4().hex)
        response = await self.__session.request("post", endpoint, json=payload)
        return Issue(response.body, self.__session)

    async def edit(
        self,
        entity_id: str,
        payload: Dict[str, Any],
        params: Optional[Dict] = None,
    ) -> Issue:
        endpoint = const.ISSUES_DIRECT_URL.format(id=entity_id)
        response = await self.__session.request(
            "patch", endpoint, params=params or {}, json=payload
        )
        return Issue(response.body, self.__session)

    async def move(
        self, entity_id: str, queue: str, params: Optional[Dict] = None
    ) -> Issue:
        endpoint = const.ISSUES_MOVE_URL.format(id=entity_id)
        params = params or {}
        params["queue"] = queue
        response = await self.__session.request(
            "post", endpoint, params=params or {}
        )
        return Issue(response.body, self.__session)

    async def count(
        self,
        filter_params: Optional[Dict] = None,
        search_query: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> Union[Dict, int]:
        endpoint = const.ISSUES_COUNT_URL.format()
        payload = {}
        if filter_params:
            payload["filter"] = filter_params
        elif search_query:
            payload["query"] = search_query

        response = await self.__session.request(
            "post", endpoint, params=params or {}, json=payload
        )
        return response.body

    async def search(
        self,
        search_request: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Collection:
        endpoint = const.ISSUES_SEARCH_URL.format()
        payload = search_request or {}
        response = await self.__session.request(
            "post", endpoint, params=params or {}, json=payload
        )
        return Collection(response, self.__session, Issue, "post", payload)
