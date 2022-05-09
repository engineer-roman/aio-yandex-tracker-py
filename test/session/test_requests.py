from json import dumps

from aio_yandex_tracker import const
from aiohttp import ClientRequest, web
from hamcrest import assert_that, equal_to


async def response_plain_cb(request: ClientRequest):
    headers = {
        "Content-type": request.headers.get("Content-type", "plain/text")
    }
    if request.method in ("POST", "PUT"):
        return web.Response(
            body=dumps({"key": "1"}, ensure_ascii=False),
            status=201,
            headers=headers,
        )
    if request.method == "DELETE":
        return web.Response(status=204, headers=headers)

    return web.Response(
        body=dumps({"key": "1"}, ensure_ascii=False),
        headers=headers,
    )


async def test_get_request(aiohttp_server, customized_session):
    get_session, session_preset = customized_session
    app = web.Application()
    app.router.add_route(
        "GET", f"/{session_preset['api_version']}/test_get", response_plain_cb
    )
    session = get_session(app._loop)

    await aiohttp_server(app, port=const.TEST_AIOHTTP_SERVER_PORT)
    resp = await session.fetch("test_get", "get")

    assert_that(resp.status, equal_to(200))


async def test_post_put_request(aiohttp_server, customized_session):
    get_session, session_preset = customized_session
    app = web.Application()
    app.router.add_route(
        "POST",
        f"/{session_preset['api_version']}/test_post",
        response_plain_cb,
    )
    app.router.add_route(
        "PUT", f"/{session_preset['api_version']}/test_put", response_plain_cb
    )
    session = get_session(app._loop)

    await aiohttp_server(app, port=const.TEST_AIOHTTP_SERVER_PORT)
    resp = await session.fetch("test_post", "post")
    assert_that(resp.status, equal_to(201))

    resp = await session.fetch("test_put", "put")
    assert_that(resp.status, equal_to(201))


async def test_delete_request(aiohttp_server, customized_session):
    get_session, session_preset = customized_session
    app = web.Application()
    app.router.add_route(
        "DELETE",
        f"/{session_preset['api_version']}/test_delete",
        response_plain_cb,
    )
    session = get_session(app._loop)

    await aiohttp_server(app, port=const.TEST_AIOHTTP_SERVER_PORT)
    resp = await session.fetch("test_delete", "delete")
    assert_that(resp.status, equal_to(204))
