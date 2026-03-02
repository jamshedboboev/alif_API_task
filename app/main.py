import asyncio

from loguru import logger

from setting import setting
from clients import rate_client

from service import Observable
from observers.console_printer import ConsolePrinterObserver
from observers.rate_alert import RateAlertObserver
from observers.file_saver import FileSaverObserver
from observers.rate_change import RateChangePercentObserver


async def main() -> None:
    subject = Observable()

    # 1) Наблюдатель, который выводит курсы
    subject.attach(ConsolePrinterObserver(setting.rates.currencies))

    # 2) Наблюдатель, который предупреждает по порогу
    subject.attach(RateAlertObserver(setting.thresholds))

    # 3) Наблюжатель, записывает обновление курсов валют в файл с временем
    subject.attach(FileSaverObserver("data/rates_history.txt"))

    # 4) Наблюдатель, который реагирует если курс изменился на процент
    subject.attach(RateChangePercentObserver(threshold_percent=setting.change_percent_threshold))

    logger.debug("Запрашиваем курсы валют...")
    client = await rate_client.get_rates()

    logger.debug("Уведомляем наблюдателей...")
    await subject.notify(client)


if __name__ == "__main__":
    asyncio.run(main())