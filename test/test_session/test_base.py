from hamcrest import assert_that, equal_to


def test_session_is_active(base_session):
    assert_that(base_session.is_active, equal_to(True))


def test_session_close(base_session):
    base_session.close()
    assert_that(base_session.is_active, equal_to(False))
