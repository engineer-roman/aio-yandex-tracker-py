from json import dumps

from aio_yandex_tracker import const
from aiohttp import ClientRequest, web


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
    resp = await session.request("get", "/test_get")

    assert resp.status == 200


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
    resp = await session.request("post", "/test_post")
    assert resp.status == 201

    resp = await session.request("put", "/test_put")
    assert resp.status == 201


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
    resp = await session.request("delete", "/test_delete")
    assert resp.status == 204
