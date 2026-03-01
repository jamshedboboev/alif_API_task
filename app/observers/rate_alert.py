from models import RatesResponse
from setting import setting, Threshold


class RateAlertObserver:
    """Предупреждает, когда курс валюты выходит за пределы указанного диапазона."""

    def __init__(self, thresholds: dict[str, Threshold]):
        self.thresholds = thresholds

    def update(self, data: RatesResponse):
        for rate, value in data.rates.items():
            if value < self.thresholds[rate].min:
                print(
                f"Alert: Валюта {rate} стала меньше указанного порога: {value} < {self.thresholds[rate].min}"
            )
                continue  # Если валюта меньше минимального порога, нет смысла проверять большее
                
            if value > self.thresholds[rate].max:
                print(
                f"Alert: Валюта {rate} стала больше указанного порога: {value} > {self.thresholds[rate].max}"
            )
                

rate_alert_observer = RateAlertObserver(setting.thresholds)