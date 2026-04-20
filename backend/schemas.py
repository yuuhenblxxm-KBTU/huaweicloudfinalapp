from datetime import datetime
import re
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

CUSTOM_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")


class LinkCreate(BaseModel):
    original_url: str
    custom_code: str | None = None

    @field_validator("original_url")
    @classmethod
    def validate_and_normalize_url(cls, value: str) -> str:
        url = value.strip()
        if not url:
            raise ValueError("URL is required")

        if "://" not in url:
            url = f"https://{url}"

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("URL must use http or https scheme")
        if not parsed.netloc:
            raise ValueError("URL host is required")
        return url

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if not CUSTOM_CODE_PATTERN.fullmatch(normalized):
            raise ValueError("Custom code must be 3-32 chars: letters, digits, _ or -")
        return normalized


class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    is_custom: bool
    created_at: datetime

    class Config:
        from_attributes = True
