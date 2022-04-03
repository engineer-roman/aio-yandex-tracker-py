import uuid
from typing import Any, Dict, Union

from aio_yandex_tracker import const, errors
from aio_yandex_tracker.session import HttpSession


class Issue:
    __original_payload = None
    __fields = {
        "self": (True, "self_url"),
        "id": (True, None),
        "key": (True, None),
        "version": (False, None),
        "lastCommentUpdatedAt": (False, "last_comment_updated_at"),
        "summary": (False, None),
        "parent": (False, None),
        "aliases": (False, None),
        "updatedBy": (False, "updated_by"),
        "description": (False, None),
        "sprint": (False, None),
        "type": (False, None),
        "priority": (False, None),
        "createdAt": (False, "created_at"),
        "followers": (False, None),
        "createdBy": (False, "created_by"),
        "votes": (False, None),
        "assignee": (False, None),
        "queue": (False, None),
        "updatedAt": (False, "updated_at"),
        "status": (False, None),
        "previousStatus": (False, "previous_status"),
        "favorite": (False, None),
    }
    key = None

    def __init__(self, payload: Dict[str, Any], session: HttpSession):
        self.__session = session
        self.original_payload = payload

    def __repr__(self):
        return f"{self.__class__.__name__} {self.key}"

    def __str__(self):
        return self.key

    async def reload(self) -> Union["Issue", bool]:
        if not self.key:
            return False
        data = await self.__session.request(
            "get", const.API_ISSUES_DIRECT_URL.format(id=self.key)
        )
        self.original_payload = data.body

    @property
    def original_payload(self) -> Dict[str, Any]:
        return self.__original_payload

    @original_payload.setter
    def original_payload(self, value: Dict[str, Any]) -> None:
        self.set_fields(value)
        self.__original_payload = value

    def set_fields(self, payload: Dict[str, Any]) -> None:
        for name, meta in self.__fields.items():
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


class Issues:
    def __init__(self, session: HttpSession):
        self.__session = session

    async def get(self, entity_id: str) -> Issue:
        endpoint = const.API_ISSUES_DIRECT_URL.format(id=entity_id)
        response = await self.__session.request("get", endpoint)
        return Issue(response.body, self.__session)

    async def create(self, payload: Dict[str, Any]) -> Issue:
        endpoint = const.API_ISSUES_URL
        payload.setdefault("unique", uuid.uuid4().hex)
        response = await self.__session.request("post", endpoint, json=payload)
        return Issue(response.body, self.__session)
