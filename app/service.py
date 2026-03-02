import asyncio
from typing import Protocol

from loguru import logger

from models import RatesResponse


class Observer(Protocol):
    """Observer handler: executes reaction when rates updated"""

    async def update(self, data: RatesResponse) -> None: ...


class Observable:
    """Manages observers and notifies them with new rate data"""

    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Subscribe observer"""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.debug(f"Observer attached: {observer}")

    def detach(self, observer: Observer) -> None:
        """Unsubscribe observer"""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"Observer detached: {observer}")

    async def notify(self, data: RatesResponse) -> None:
        """Notify all observers (async)"""
        observers_snapshot = list(self._observers)
        if not observers_snapshot:
            logger.debug("No observers to notify")
            return

        logger.info(f"Notifying observers: count={len(observers_snapshot)}")

        # Параллельно уведомляем всех, но не падаем всем notify, если один observer упал
        results = await asyncio.gather(
            *(observer.update(data) for observer in observers_snapshot),
            return_exceptions=True,
        )

        for obs, res in zip(observers_snapshot, results, strict=False):
            if isinstance(res, BaseException):
                logger.exception("Observer failed: {}", obs)