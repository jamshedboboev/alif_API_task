import asyncio
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from clients import RateClient
from models import RatesResponse


class _RespCM:
    """Async context manager wrapper for mocked aiohttp response."""
    def __init__(self, resp: Mock):
        self._resp = resp

    async def __aenter__(self) -> Mock:
        return self._resp

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


@pytest.mark.asyncio
async def test_get_rates_success(monkeypatch):
    client = RateClient(url="http://example", timeout=1)

    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json = AsyncMock(
        return_value={
            "base_code": "USD",
            "time_last_update_utc": "Sat, 28 Feb 2026 00:02:32 +0000",
            "rates": {"TJS": 10.5, "RUB": 91.0, "EUR": 0.92},
        }
    )

    session = Mock()
    session.get = Mock(return_value=_RespCM(resp))

    monkeypatch.setattr(client, "_get_session", AsyncMock(return_value=session))

    data = await client.get_rates(symbols=["TJS", "RUB"], base="USD")

    assert isinstance(data, RatesResponse)
    assert data.base == "USD"
    assert data.rates["TJS"] == 10.5
    assert data.rates["RUB"] == 91.0


@pytest.mark.asyncio
async def test_get_rates_empty_symbols_raises():
    client = RateClient(url="http://example", timeout=1)

    with pytest.raises(ValueError):
        await client.get_rates(symbols=[], base="USD")


@pytest.mark.asyncio
async def test_get_rates_base_mismatch_raises(monkeypatch):
    client = RateClient(url="http://example", timeout=1)

    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json = AsyncMock(
        return_value={
            "base_code": "EUR",
            "time_last_update_utc": "x",
            "rates": {"TJS": 10.5},
        }
    )

    session = Mock()
    session.get = Mock(return_value=_RespCM(resp))
    monkeypatch.setattr(client, "_get_session", AsyncMock(return_value=session))

    with pytest.raises(ValueError):
        await client.get_rates(symbols=["TJS"], base="USD")


@pytest.mark.asyncio
async def test_get_rates_missing_currency_raises(monkeypatch):
    client = RateClient(url="http://example", timeout=1)

    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json = AsyncMock(
        return_value={
            "base_code": "USD",
            "time_last_update_utc": "x",
            "rates": {"EUR": 0.92},
        }
    )

    session = Mock()
    session.get = Mock(return_value=_RespCM(resp))
    monkeypatch.setattr(client, "_get_session", AsyncMock(return_value=session))

    with pytest.raises(KeyError):
        await client.get_rates(symbols=["TJS"], base="USD")


@pytest.mark.asyncio
async def test_get_rates_retries_then_success(monkeypatch):
    client = RateClient(url="http://example", timeout=1)

    # sleep не должен реально ждать
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json = AsyncMock(
        return_value={
            "base_code": "USD",
            "time_last_update_utc": "x",
            "rates": {"TJS": 9.5},
        }
    )

    session = Mock()
    # 1-я попытка падает, 2-я успешна
    session.get = Mock(side_effect=[
        aiohttp.ClientError("boom"),
        _RespCM(resp),
    ])

    monkeypatch.setattr(client, "_get_session", AsyncMock(return_value=session))

    data = await client.get_rates(symbols=["TJS"], base="USD")
    assert data.rates["TJS"] == 10.5
    assert asyncio.sleep.await_count == 1


@pytest.mark.asyncio
async def test_get_rates_retries_fail(monkeypatch):
    client = RateClient(url="http://example", timeout=1)

    monkeypatch.setattr(asyncio, "sleep", AsyncMock())

    session = Mock()
    session.get = Mock(side_effect=[
        aiohttp.ClientError("1"),
        aiohttp.ClientError("2"),
        aiohttp.ClientError("3"),
    ])

    monkeypatch.setattr(client, "_get_session", AsyncMock(return_value=session))

    with pytest.raises(RuntimeError):
        await client.get_rates(symbols=["TJS"], base="USD")

    assert asyncio.sleep.await_count == 2  # между 1-2 и 2-3