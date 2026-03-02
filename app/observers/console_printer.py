from typing import Iterable
from models import RatesResponse

from loguru import logger

from models import RatesResponse


class ConsolePrinterObserver:
    """Prints selected rates to console in a readable format"""

    def __init__(self, currencies: Iterable[str]) -> None:
        self._currencies = [c.upper() for c in currencies]

    async def update(self, data: RatesResponse) -> None:
        ts = getattr(data, "updated_utc", None)

        header = f"Rates (base={data.base})"
        if ts:
            header += f" | updated: {ts}"

        lines: list[str] = [header]
        for code in self._currencies:
            value = data.rates.get(code)
            if value is None:
                lines.append(f"  {data.base} → {code}: N/A")
            else:
                lines.append(f"  {data.base} → {code}: {value:.6f}")
        lines.append("-" * 40)

        logger.info("\n" + "\n".join(lines))