import uuid
from typing import Any, Dict, Optional, Type, Union

from aio_yandex_tracker import const, errors
from aio_yandex_tracker.models.http import HttpResponse
from aio_yandex_tracker.session import HttpSession

# from yarl import URL


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
        for name, meta in self._fields.items():
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
        self._session = session
        self._entity_cls = entity_cls
        self._parent_id = parent_id
        self._url = response.url
        self._url_params = {**self._url.query}
        self._endpoint = response.url.path[
            len(session.api_version) + 2 :  # noqa E203
        ]
        self._request_method = method
        self._request_payload = payload or {}


class PaginatedCollection(Collection):
    def __init__(
        self,
        response: HttpResponse,
        session: HttpSession,
        entity_cls: Type[BaseEntity],
        method: str,
        parent_id: Optional[str] = None,
        payload: Optional[Dict] = None,
    ):
        super(PaginatedCollection, self).__init__(
            response,
            session,
            entity_cls,
            method,
            parent_id,
            payload,
        )
        self._page = int(self._url_params.get("page", 1))
        self._total_pages = int(response.headers.get("X-Total-Pages", 0))
        self._total_entities = int(response.headers.get("X-Total-Count", 0))

    @property
    def page(self) -> int:
        return self._page

    @property
    def total_pages(self) -> int:
        return self._total_pages

    @property
    def total_entities(self) -> int:
        return self._total_entities

    async def load_next(self):
        return await self.load_page_num(self._page + 1)

    async def load_prev(self):
        return await self.load_page_num(self._page - 1)

    async def load_page_num(self, page: int):
        if page < 1 or page > self._total_pages or page == self._page:
            raise errors.PaginationProhibitedError(
                f"Cannot turn page to {page}"
            )
        if self._page >= self.total_pages:
            raise errors.PaginationProhibitedError("No next page found")
        response = await self._session.fetch(
            self._endpoint,
            self._request_method,
            params={**self._url_params, "page": page},
            json=self._request_payload,
        )
        return self.__class__(
            response,
            self._session,
            self._entity_cls,
            self._request_method,
            self._request_payload,
        )


class RestrictedPaginatedCollection(Collection):
    def __init__(
        self,
        response: HttpResponse,
        session: HttpSession,
        entity_cls: Type[BaseEntity],
        method: str,
        parent_id: Optional[str] = None,
        payload: Optional[Dict] = None,
    ):
        super(RestrictedPaginatedCollection, self).__init__(
            response,
            session,
            entity_cls,
            method,
            parent_id,
            payload,
        )
        links = session.serialize_headers_links(response.headers)
        self._first_page_url = links.get("first")
        self._next_page_url = links.get("next")

    async def load_first(self):
        if not self._first_page_url:
            raise errors.PaginationProhibitedError("No first page found")
        return await self.__load_page(self._first_page_url)

    async def load_next(self):
        if not self._next_page_url:
            raise errors.PaginationProhibitedError("No next page found")
        return await self.__load_page(self._next_page_url)

    async def __load_page(self, url: str):
        response = await self._session.request(
            url,
            self._request_method,
            json=self._request_payload,
        )
        return self.__class__(
            response,
            self._session,
            self._entity_cls,
            self._request_method,
            self._request_payload,
        )


ANY_COLLECTION_TYPE = Union[
    Collection, PaginatedCollection, RestrictedPaginatedCollection
]


def create_collection(
    response: HttpResponse,
    session: HttpSession,
    entity_cls: Type[BaseEntity],
    method: str,
    parent_id: Optional[str] = None,
    payload: Optional[Dict] = None,
) -> ANY_COLLECTION_TYPE:
    collection_links_map = [
        (("first", "seek"), PaginatedCollection),
        (
            (
                "first",
                "next",
            ),
            RestrictedPaginatedCollection,
        ),
    ]
    links = session.serialize_headers_links(response.headers)
    response_link_types = set(links.keys())
    for link_types, obj in collection_links_map:
        if not (set(link_types) - response_link_types):
            return obj(
                response, session, entity_cls, method, parent_id, payload
            )
    else:
        return Collection(
            response, session, entity_cls, method, parent_id, payload
        )


class Link(BaseEntity):
    _fields = {
        "self": (True, "self_url"),
        "id": (True, None),
        "type": (True, None),
        "direction": (True, None),
        "object": (True, None),
        "createdAt": (True, "created_at"),
        "updatedAt": (True, "updated_at"),
        "createdBy": (True, "created_by"),
        "updatedBy": (True, "updated_by"),
        "assignee": (False, None),
        "status": (False, None),
    }
    id = None

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.id}>"

    def __str__(self):
        return self.id


class Priority(BaseEntity):
    _fields = {
        "self": (True, "self_url"),
        "id": (True, None),
        "key": (True, None),
        "name": (True, None),
        "description": (False, None),
        "order": (True, None),
        "version": (False, None),
    }
    key = None

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.key}>"

    def __str__(self):
        return self.key


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
    ) -> ANY_COLLECTION_TYPE:
        endpoint = const.TRANSITIONS_EXEC_URL.format(
            id=self.__parent_id, transition_id=self.id
        )
        payload = payload or {}
        if comment:
            payload["comment"] = comment

        response = await self._session.fetch(endpoint, "post", payload)
        return create_collection(
            response,
            self._session,
            Transition,
            "post",
            self.__parent_id,
            payload,
        )


class IssueChangelog(BaseEntity):
    _fields = {
        "self": (True, "self_url"),
        "type": (True, None),
        "id": (True, None),
        "issue": (True, None),
        "updatedAt": (False, "updated_at"),
        "updatedBy": (False, "updated_by"),
        "transport": (True, None),
        "fields": (False, None),
    }
    type = None

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.type}>"

    def __str__(self):
        return self.type


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
        endpoint = const.ISSUES_DIRECT_URL.format(id=self.key)
        data = await self._session.fetch(endpoint, "get")
        self.original_payload = data.body

    async def links(self) -> ANY_COLLECTION_TYPE:
        endpoint = const.LINKS_URL.format(id=self.key)
        response = await self._session.fetch(endpoint, "get")
        return create_collection(
            response, self._session, Link, "get", self.key
        )

    async def add_link(self, relation_type: str, issue: str) -> Link:
        endpoint = const.LINKS_URL.format(id=self.key)
        payload = {
            "relationship": relation_type,
            "issue": issue,
        }
        response = await self._session.fetch(endpoint, "post", json=payload)
        return Link(response.body, self._session)

    async def delete_link(self, link_id: int) -> None:
        endpoint = const.LINKS_DIRECT_URL.format(id=self.key, link_id=link_id)
        await self._session.fetch(endpoint, "delete")

    async def transitions(self) -> ANY_COLLECTION_TYPE:
        endpoint = const.TRANSITIONS_URL.format(id=self.key)
        response = await self._session.fetch(endpoint, "get")
        return create_collection(
            response, self._session, Transition, "get", self.key
        )

    async def apply_transition(
        self,
        transition_id: str,
        payload: Optional[Dict] = None,
        comment: Optional[str] = None,
    ) -> ANY_COLLECTION_TYPE:
        endpoint = const.TRANSITIONS_EXEC_URL.format(
            id=self.key, transition_id=transition_id
        )
        payload = payload or {}
        if comment:
            payload["comment"] = comment

        response = await self._session.fetch("post", endpoint, json=payload)
        return create_collection(
            response, self._session, Transition, "post", self.key, payload
        )

    async def changelog(
        self, params: Optional[Dict] = None
    ) -> ANY_COLLECTION_TYPE:
        endpoint = const.CHANGELOG_URL.format(id=self.key)
        response = await self._session.fetch(
            endpoint, "get", params=params or {}
        )
        return create_collection(
            response, self._session, IssueChangelog, "get", self.key
        )


class Priorities:
    __single_entity_cls = Priority

    def __init__(self, session: HttpSession):
        self.__session = session

    async def get(self, params: Optional[Dict] = None) -> ANY_COLLECTION_TYPE:
        endpoint = const.PRIORITIES_URL
        response = await self.__session.request(
            "get", endpoint, params=params or {}
        )
        return create_collection(response, self.__session, Priority, "get")


class Issues:
    __single_entity_cls = Issue

    def __init__(self, session: HttpSession):
        self.__session = session

    async def get(
        self, entity_id: str, params: Optional[Dict] = None
    ) -> Issue:
        endpoint = const.ISSUES_DIRECT_URL.format(id=entity_id)
        response = await self.__session.fetch(
            endpoint, "get", params=params or {}
        )
        return Issue(response.body, self.__session)

    async def transitions(self, entity_id: str) -> ANY_COLLECTION_TYPE:
        endpoint = const.TRANSITIONS_URL.format(id=entity_id)
        response = await self.__session.fetch(endpoint, "get")
        return create_collection(
            response, self.__session, Transition, "get", entity_id
        )

    async def create(self, payload: Dict[str, Any]) -> Issue:
        endpoint = const.ISSUES_URL
        payload.setdefault("unique", uuid.uuid4().hex)
        response = await self.__session.fetch(endpoint, "post", json=payload)
        return Issue(response.body, self.__session)

    async def edit(
        self,
        entity_id: str,
        payload: Dict[str, Any],
        params: Optional[Dict] = None,
    ) -> Issue:
        endpoint = const.ISSUES_DIRECT_URL.format(id=entity_id)
        response = await self.__session.fetch(
            endpoint, "patch", params=params or {}, json=payload
        )
        return Issue(response.body, self.__session)

    async def move(
        self, entity_id: str, queue: str, params: Optional[Dict] = None
    ) -> Issue:
        endpoint = const.ISSUES_MOVE_URL.format(id=entity_id)
        params = params or {}
        params["queue"] = queue
        response = await self.__session.fetch(
            endpoint, "post", params=params or {}
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

        response = await self.__session.fetch(
            endpoint, "post", params=params or {}, json=payload
        )
        return response.body

    async def search(
        self,
        search_request: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> ANY_COLLECTION_TYPE:
        endpoint = const.ISSUES_SEARCH_URL.format()
        payload = search_request or {}
        response = await self.__session.fetch(
            endpoint, "post", params=params or {}, json=payload
        )
        return create_collection(
            response, self.__session, Issue, "post", payload
        )
