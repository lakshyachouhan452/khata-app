from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionStatus, TransactionType


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="'gave_credit' or 'received_payment'")
    due_date: Optional[datetime] = Field(None, description="Due date for credit recovery")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, description="Transaction status")


class TransactionCreate(TransactionBase):
    customer_id: int = Field(..., description="ID of the customer")


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
