from hamcrest import assert_that, equal_to


def test_session_is_active(base_session, event_loop):
    session = base_session(loop=event_loop)
    assert_that(session.is_active, equal_to(True))


def test_session_close(base_session, event_loop):
    session = base_session(loop=event_loop)
    session.close()
    assert_that(session.is_active, equal_to(False))
