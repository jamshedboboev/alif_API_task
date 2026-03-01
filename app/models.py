from pydantic import BaseModel, Field


class RatesResponse(BaseModel):
    base: str = Field(..., description="Базовая валюта (ожидается USD)")
    updated_utc: str | None = Field(None, description="Время последнего обновления, UTC")
    rates: dict[str, float] = Field(..., description="Курсы валют относительно base")