import time
import requests

from typing import Iterable

from .models import RatesResponse
from .setting import setting


class RateClient:
    """
    Клиент для получения курсов валют из ExchangeRate-API.
    """

    def __init__(self, url: str, timeout: float):
        self._url = url
        self._timeout = timeout
        self._session = requests.Session()

    def get_rates(self, symbols: Iterable[str] = setting.rates.currencies, base: str = setting.rates.base_currency) -> RatesResponse:
        """
        Получает курсы заданных валют относительно base.

        :param symbols: список валют (по умолчанию TJS, RUB, EUR)
        :param base: базовая валюта, относительно которой считаются курсы (по умолчанию USD)
        """
        symbols_set = {s.upper() for s in symbols}
        if not symbols_set:
            raise ValueError("symbols должен содержать хотя бы одну валюту")

        for i in range(3):
            try:
                resp = self._session.get(self._url, timeout=self._timeout)
                break  # если запрос успешен — выходим из цикла
            except requests.RequestException as e:
                if i < 2:
                    time.sleep(1)
                else:
                    raise RuntimeError(f"API недоступен после 3 попыток: {e}") from e
                
        resp.raise_for_status()  # type:ignore
        data = resp.json()       # type:ignore

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
    
rate_client = RateClient(str(setting.api.url), setting.api.timeout_seconds)