import asyncio

from loguru import logger

from setting import setting
from clients import rate_client
from service import Observable
from observers.console_printer import ConsolePrinterObserver
from observers.rate_alert import RateAlertObserver


async def main() -> None:
    subject = Observable()

    # 1) Наблюдатель, который выводит курсы
    subject.attach(ConsolePrinterObserver(setting.rates.currencies))

    # 2) Наблюдатель, который предупреждает по порогу
    subject.attach(RateAlertObserver(setting.thresholds))

    logger.debug("Запрашиваем курсы валют...")
    client = await rate_client.get_rates()

    logger.debug("Уведомляем наблюдателей...")
    await subject.notify(client)


if __name__ == "__main__":
    asyncio.run(main())