from setting import setting
from models import RatesResponse
from observers.console_printer import ConsolePrinterObserver
from observers.rate_alert import RateAlertObserver

rate = RatesResponse(base="USD", updated_utc=None, rates={"TJS": 11, "RUB": 81})

ConsolePrinterObserver(("TJS", "RUB")).update(rate)

RateAlertObserver(setting.thresholds).update(rate)