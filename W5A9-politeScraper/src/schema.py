import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

PRICE_PATTERN = re.compile(r"\d+(?:\.\d+)?")


def normalize_price(price_text):
    match = PRICE_PATTERN.search(price_text or "")
    if match is None:
        raise ValueError(f"no number found in price_text {price_text!r}")
    return float(match.group(0))


class Book(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    product_url: str
    price_text: str = Field(min_length=1)
    price_gbp: float = Field(ge=0)
    availability_text: str = Field(min_length=1)
    rating_text: str = Field(min_length=1)
    description: str | None = None
    source_page: str
    fetched_at: str

    @field_validator("product_url", "source_page")
    @classmethod
    def must_be_absolute_https(cls, value):
        if not value.startswith("https://"):
            raise ValueError(f"expected an absolute https:// URL, got {value!r}")
        return value

    @field_validator("fetched_at")
    @classmethod
    def must_be_utc_timestamp(cls, value):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
            raise ValueError(f"expected a UTC timestamp like 2026-08-06T10:00:00Z, got {value!r}")
        return value


def build(raw):
    record = dict(raw)
    record["price_gbp"] = normalize_price(record.get("price_text"))
    return Book(**record)
