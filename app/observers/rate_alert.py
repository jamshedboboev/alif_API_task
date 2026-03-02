from loguru import logger

from models import RatesResponse
from setting import Threshold


class RateAlertObserver:
    """Предупреждает, когда курс валюты выходит за пределы указанного диапазона."""

    def __init__(self, thresholds: dict[str, Threshold]):
        self.thresholds = thresholds

    async def update(self, data: RatesResponse):
        for rate, value in data.rates.items():
            if value < self.thresholds[rate].min:
                logger.warning(f"Alert >> Валюта {rate} стала меньше указанного порога: {value} < {self.thresholds[rate].min}")
                continue  # Если валюта меньше минимального порога, нет смысла проверять большее

            if value > self.thresholds[rate].max:
                logger.warning(f"Alert >> Валюта {rate} стала больше указанного порога: {value} > {self.thresholds[rate].max}")