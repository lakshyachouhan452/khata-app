from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import TransactionStatus, TransactionType


# ----------------------------------------------------
# Transaction Schemas
# ----------------------------------------------------
class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Transaction amount in currency units")
    transaction_type: TransactionType = Field(..., description="'gave_credit' or 'received_payment'")
    due_date: Optional[datetime] = Field(None, description="Due date for credit recovery (optional)")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, description="Transaction status")


class TransactionCreate(TransactionBase):
    customer_id: int = Field(..., description="ID of the customer this transaction belongs to")


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    transaction_type: Optional[TransactionType] = None
    due_date: Optional[datetime] = None
    status: Optional[TransactionStatus] = None


class TransactionResponse(TransactionBase):
    id: int
    customer_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------
# Customer Schemas
# ----------------------------------------------------
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


# ----------------------------------------------------
# Specialized Endpoint Schemas
# ----------------------------------------------------
class UpcomingExpectedAmountResponse(BaseModel):
    total_expected_amount: Decimal = Field(..., description="Sum of credit due within the next 7 days")
    start_date: datetime = Field(..., description="Start of the 7-day query window")
    end_date: datetime = Field(..., description="End of the 7-day query window")
    transaction_count: int = Field(..., description="Number of credit transactions due in this window")
    transactions: List[TransactionResponse] = Field(default_factory=list)


class OverdueCustomerItem(BaseModel):
    customer: CustomerResponse
    overdue_amount: Decimal = Field(..., description="Total pending/overdue credit amount that has lapsed")
    overdue_transactions: List[TransactionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
