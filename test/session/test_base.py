from hamcrest import assert_that, equal_to


async def test_session_is_active(base_session, event_loop):
    session = base_session(loop=event_loop)
    assert_that(session.is_closed, equal_to(True))
    await session.close()


async def test_session_close(base_session, event_loop):
    session = base_session(loop=event_loop)
    await session.close()
    assert_that(session.is_closed, equal_to(True))
