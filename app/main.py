from setting import setting
from clients import rate_client
from service import Observable
from observers.console_printer import ConsolePrinterObserver
from observers.rate_alert import RateAlertObserver


def main() -> None:
    client = rate_client.get_rates()
    subject = Observable()

    # 1) Наблюдатель, который выводит курсы
    subject.attach(ConsolePrinterObserver(setting.rates.currencies))

    # 2) Наблюдатель, который предупреждает по порогу
    subject.attach(RateAlertObserver(setting.thresholds))

    # Получаем данные и уведомляем наблюдателей
    subject.notify(client)


if __name__ == "__main__":
    main()