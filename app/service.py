from typing import Protocol

from models import RatesResponse


class Observer(Protocol):
    """Observer handler: executes reaction when rates updated"""

    def update(self, data: RatesResponse) -> None: ...


class Observable:
    """Manages observers and notifies them with new rate data"""

    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Subscribe observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Unsubscribe observe"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, data: RatesResponse) -> None:
        """Notify all observers"""
        for observer in list(self._observers):
            observer.update(data)