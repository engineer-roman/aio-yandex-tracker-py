from aio_yandex_tracker import const
from aio_yandex_tracker.tracker import YandexTracker
from hamcrest import assert_that, equal_to


async def test_yatracker_cm():
    async with YandexTracker(
        const.TEST_TRACKER_TOKEN, const.TEST_TRACKER_ORG_ID
    ) as tracker:
        pass
    assert_that(tracker.is_closed, equal_to(True))
