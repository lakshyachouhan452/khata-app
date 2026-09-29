from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.customer import CustomerResponse
from app.schemas.transaction import TransactionResponse


class UpcomingExpectedAmountResponse(BaseModel):
    total_expected_amount: Decimal = Field(..., description="Sum of credit due within next 7 days")
    start_date: datetime = Field(..., description="Start of window")
    end_date: datetime = Field(..., description="End of window")
    transaction_count: int = Field(..., description="Count of due transactions")
    transactions: List[TransactionResponse] = Field(default_factory=list)


class OverdueCustomerItem(BaseModel):
    customer: CustomerResponse
    overdue_amount: Decimal = Field(..., description="Total overdue amount")
    overdue_transactions: List[TransactionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
