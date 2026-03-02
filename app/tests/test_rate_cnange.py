from unittest.mock import Mock

import pytest

from observers.rate_change import RateChangePercentObserver
from models import RatesResponse


@pytest.mark.asyncio
async def test_change_percent_first_update_no_reaction(monkeypatch):
    warn = Mock()
    monkeypatch.setattr("observers.rate_change.logger.warning", warn)

    obs = RateChangePercentObserver(threshold_percent=5.0)

    await obs.update(RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.0}))
    assert warn.call_count == 0


@pytest.mark.asyncio
async def test_change_percent_below_threshold_no_reaction(monkeypatch):
    warn = Mock()
    monkeypatch.setattr("observers.rate_change.logger.warning", warn)

    obs = RateChangePercentObserver(threshold_percent=5.0)

    await obs.update(RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.0}))
    await obs.update(RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.4}))

    assert warn.call_count == 0


@pytest.mark.asyncio
async def test_change_percent_above_threshold_reacts(monkeypatch):
    warn = Mock()
    monkeypatch.setattr("observers.rate_change.logger.warning", warn)

    obs = RateChangePercentObserver(threshold_percent=5.0)

    await obs.update(RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.0}))
    await obs.update(RatesResponse(base="USD", updated_utc="x", rates={"TJS": 9.6}))

    assert warn.call_count == 1