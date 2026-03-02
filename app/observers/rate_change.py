from loguru import logger

from models import RatesResponse


class RateChangePercentObserver:
    """
    Отслеживает изменения и реагирует только если курс изменился
    более чем на заданный процент.
    """

    def __init__(self, threshold_percent: float) -> None:
        self._threshold_percent = threshold_percent
        self._last_rates: dict[str, float] = {}

    async def update(self, data: RatesResponse) -> None:
        for code, new_value in data.rates.items():
            if code not in self._last_rates:
                self._last_rates[code] = new_value
                continue

            old_value = self._last_rates[code]

            # защита от деления на 0
            if old_value == 0:
                self._last_rates[code] = new_value
                continue

            diff_percent = abs((new_value - old_value) / old_value) * 100.0

            if diff_percent > self._threshold_percent:
                logger.warning(
                    f"Rate change >> {code}: {old_value:.6f} -> {new_value:.6f} ({diff_percent:.2f}% > {self._threshold_percent}%)",
                )

            self._last_rates[code] = new_value