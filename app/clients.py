import asyncio
from typing import Iterable, Optional

import aiohttp
from loguru import logger

from models import RatesResponse
from setting import setting


class RateClient:
    """
    Асинхронный клиент для получения курсов валют из ExchangeRate-API.
    """

    def __init__(self, url: str, timeout: float):
        self._url = url
        self._timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

        logger.debug("RateClient инициализирован: url={}, timeout={}", url, timeout)

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Возвращает активную ClientSession (создаёт при необходимости).
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
            logger.debug("Создана новая aiohttp ClientSession")
        return self._session

    async def aclose(self) -> None:
        """
        Закрывает HTTP-сессию, если она была создана.
        """
        if self._session is not None and not self._session.closed:
            await self._session.close()
            logger.info("HTTP-сессия закрыта")

    async def __aenter__(self) -> "RateClient":
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def get_rates(
        self,
        symbols: Iterable[str] = setting.rates.currencies,
        base: str = setting.rates.base_currency,
    ) -> RatesResponse:
        """
        Получает курсы заданных валют относительно base.

        :param symbols: список валют (по умолчанию TJS, RUB, EUR)
        :param base: базовая валюта (по умолчанию USD)
        """
        symbols_set = {s.upper() for s in symbols}
        if not symbols_set:
            logger.error("Передан пустой список symbols")
            raise ValueError("symbols должен содержать хотя бы одну валюту")

        logger.info(
            "Запрос курсов валют: base={}, symbols={}",
            base,
            sorted(symbols_set),
        )

        session = await self._get_session()

        last_exc: Optional[BaseException] = None

        for attempt in range(1, 4):
            try:
                logger.debug("Попытка запроса к API №{}", attempt)

                async with session.get(self._url) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

                logger.debug("Ответ от API успешно получен")
                break

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exc = e
                logger.warning(
                    "Ошибка при обращении к API (попытка {}): {}",
                    attempt,
                    str(e),
                )

                if attempt < 3:
                    await asyncio.sleep(1)
                else:
                    logger.exception("API недоступен после 3 попыток")
                    raise RuntimeError(
                        f"API недоступен после 3 попыток: {e}"
                    ) from e

        base_code = data["base_code"]
        if base_code != base:
            logger.error(
                "Несоответствие base: ожидалось {}, получено {}",
                base,
                base_code,
            )
            raise ValueError(
                f"Ожидалось base={base}, но API вернул base_code={base_code}"
            )

        rates = data.get("rates", {})
        missing = [code for code in symbols_set if code not in rates]
        if missing:
            logger.error("В ответе API отсутствуют валюты: {}", missing)
            raise KeyError(f"В ответе API отсутствуют валюты: {missing}")

        filtered_rates = {code: float(rates[code]) for code in symbols_set}

        logger.info(
            "Курсы успешно получены. base={}, updated={}, currencies={}",
            base_code,
            data.get("time_last_update_utc"),
            list(filtered_rates.keys()),
        )

        return RatesResponse(
            base=base_code,
            updated_utc=data.get("time_last_update_utc"),
            rates=filtered_rates,
        )


rate_client = RateClient(
    str(setting.api.url),
    setting.api.timeout_seconds,
)