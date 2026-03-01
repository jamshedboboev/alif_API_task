import requests

from typing import Iterable

from .models import RatesResponse


class RateClient:
    """
    Клиент для получения курсов валют из ExchangeRate-API.
    """

    def __init__(self, url: str, timeout: float = 5.0):
        self._url = url
        self._timeout = timeout
        self._session = requests.Session()

    def get_rates(self, symbols: Iterable[str] = ("TJS", "RUB", "EUR"), base: str = "USD") -> RatesResponse:
        """
        Получает курсы заданных валют относительно base.

        :param symbols: список валют (по умолчанию TJS, RUB, EUR)
        :param base: базовая валюта, относительно которой считаются курсы (по умолчанию USD)
        """
        symbols_set = {s.upper() for s in symbols}
        if not symbols_set:
            raise ValueError("symbols должен содержать хотя бы одну валюту")

        resp = self._session.get(self._url, timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()

        base_code = data["base_code"]
        if base_code != base:
            raise ValueError(f"Ожидалось base={base}, но API вернул base_code={base_code}")

        rates = data.get("rates", {})
        missing = [i for i in symbols_set if i not in rates]
        if missing:
            raise KeyError(f"В ответе API отсутствуют валюты: {missing}")

        filtered_rates = {i: float(rates[i]) for i in symbols_set}

        return RatesResponse(
            base=base_code,
            updated_utc=data.get("time_last_update_utc"),
            rates=filtered_rates,
        )
    
rate_client = RateClient("https://open.er-api.com/v6/latest/USD")