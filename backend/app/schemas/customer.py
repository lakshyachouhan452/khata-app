from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.schemas.transaction import TransactionResponse


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Customer name")
    phone: str = Field(
        ...,
        min_length=7,
        max_length=20,
        pattern=r"^\+?[0-9\s\-()]{7,20}$",
        description="Customer contact phone number",
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=7, max_length=20, pattern=r"^\+?[0-9\s\-()]{7,20}$")


class CustomerResponse(CustomerBase):
    id: int
    total_outstanding: Decimal

    model_config = ConfigDict(from_attributes=True)


class CustomerDetailResponse(CustomerResponse):
    transactions: List[TransactionResponse] = []

    model_config = ConfigDict(from_attributes=True)
