from aio_yandex_tracker.session import HttpSession


class Issue:
    def __init__(self, session: HttpSession):
        self.__session = session
        self.__base_url = "/issues"
        self.__direct_url = f"{self.__base_url}/{{id}}"

    async def get(self, entity_id):
        endpoint = self.__direct_url.format(id=entity_id)
        response = await self.__session.request("get", endpoint)
        return response
