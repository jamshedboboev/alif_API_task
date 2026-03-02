import asyncio
from datetime import datetime
from pathlib import Path

from loguru import logger

from models import RatesResponse


class FileSaverObserver:
    """
    Сохраняет каждое обновление курсов в файл с таймстемпом (накопительно).
    """

    def __init__(self, file_path: str) -> None:
        self._path = Path(file_path)

    async def update(self, data: RatesResponse) -> None:
        timestamp = datetime.utcnow().isoformat()

        lines = [f"[{timestamp}] base={data.base}"]

        for code, value in data.rates.items():
            lines.append(f"  {data.base} -> {code}: {value:.6f}")

        lines.append("-" * 40)
        content = "\n".join(lines) + "\n"

        await asyncio.to_thread(self._append_to_file, content)
        logger.info(f"Данные сохранены в файл: {self._path}")

    def _append_to_file(self, content: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(content)