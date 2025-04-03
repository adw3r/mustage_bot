import datetime as dt
from typing import Any

from pydantic import BaseModel, field_validator


class PaymentBase(BaseModel):
    id: Any


class PaymentCreate(BaseModel):
    created_at: dt.date | str
    comment: str
    amount_uah: float
    @field_validator("created_at", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            dt.datetime.strptime(value, "%d.%m.%Y").date()

        return value


class PaymentPatch(BaseModel):
    comment: str | None = None
    amount_uah: float | None = None
    payment_id: int


class GetPayments(BaseModel):
    created_at_first: str
    created_at_second: str
    @field_validator("created_at_first", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            dt.datetime.strptime(value, "%d.%m.%Y").date()

        return value
    @field_validator("created_at_second", mode="before")
    @classmethod
    def parse_date_second(cls, value):
        if isinstance(value, str):
            dt.datetime.strptime(value, "%d.%m.%Y").date()

        return value
