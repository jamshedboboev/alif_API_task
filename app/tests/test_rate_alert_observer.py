from unittest.mock import AsyncMock

import pytest

from service import Observable
from models import RatesResponse


@pytest.mark.asyncio
async def test_notify_calls_all_observers():
    subject = Observable()

    o1 = AsyncMock()
    o2 = AsyncMock()

    subject.attach(o1)
    subject.attach(o2)

    data = RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.4})

    await subject.notify(data)

    o1.update.assert_awaited_once_with(data)
    o2.update.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_notify_does_not_stop_if_one_observer_fails():
    subject = Observable()

    ok = AsyncMock()
    bad = AsyncMock()
    bad.update.side_effect = RuntimeError("fail")

    subject.attach(bad)
    subject.attach(ok)

    data = RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.4})

    await subject.notify(data)

    bad.update.assert_awaited_once()
    ok.update.assert_awaited_once()