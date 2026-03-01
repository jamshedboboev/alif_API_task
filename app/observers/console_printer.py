from typing import Iterable
from models import RatesResponse


class ConsolePrinterObserver:
    """Prints selected rates to console in a readable format."""

    def __init__(self, currencies: Iterable[str]) -> None:
        self._currencies = currencies

    def update(self, data: RatesResponse) -> None:
        ts = getattr(data, "time_last_update_utc", None)  # если поле есть в модели
        header = f"Rates (base={data.base})"
        if ts:
            header += f" | updated: {ts}"

        print(header)
        for code in self._currencies:
            value = data.rates.get(code)
            if value is None:
                print(f"  {data.base} → {code}: N/A")
            else:
                print(f"  {data.base} → {code}: {value:.6f}")
        print("-" * 40)