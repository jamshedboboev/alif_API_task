import yaml
from pathlib import Path

from pydantic import BaseModel, HttpUrl, Field, field_validator, model_validator


class ApiConfig(BaseModel):
    """API configuration."""
    url: HttpUrl
    timeout_seconds: int = Field(
        default=5,
        description="HTTP timeout in seconds",
    )


class RatesConfig(BaseModel):
    """Rates polling configuration."""
    base_currency: str = Field(min_length=3, max_length=3)
    currencies: list[str]
    interval_seconds: int

    @field_validator("base_currency")
    @classmethod
    def validate_base_currency(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("currencies")
    @classmethod
    def validate_currencies(cls, v: list[str]) -> list[str]:
        cleaned = [c.strip().upper() for c in v]

        if len(set(cleaned)) != len(cleaned):
            raise ValueError("Duplicate currency codes are not allowed.")

        for currency in cleaned:
            if len(currency) != 3 or not currency.isalpha():
                raise ValueError(
                    f"Invalid currency code: {currency}. "
                    "Expected 3-letter ISO code like 'USD'."
                )

        return cleaned


class Threshold(BaseModel):
    """Inclusive rate bounds for alerts."""
    min: float
    max: float

    @model_validator(mode="after")
    def check_bounds(self) -> "Threshold":
        if self.min >= self.max:
            raise ValueError(
                f"Invalid threshold: min ({self.min}) must be less than max ({self.max})"
            )
        return self


class AppConfig(BaseModel):
    """Root application configuration."""
    api: ApiConfig
    rates: RatesConfig
    thresholds: dict[str, Threshold] = Field(default_factory=dict)

    @field_validator("thresholds")
    @classmethod
    def normalize_threshold_keys(cls, v: dict[str, Threshold]) -> dict[str, Threshold]:
        return {k.strip().upper(): val for k, val in v.items()}

    @model_validator(mode="after")
    def validate_thresholds(self) -> "AppConfig":
        configured = set(self.rates.currencies)
        extra = set(self.thresholds.keys()) - configured
        if extra:
            raise ValueError(
                "thresholds contain currencies not listed in rates.currencies: "
                + ", ".join(sorted(extra))
            )
        return self


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    """
    Load and validate external YAML configuration.
    """
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path.resolve()}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(raw)


setting = load_config()