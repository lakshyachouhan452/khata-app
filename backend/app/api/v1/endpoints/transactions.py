from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.transaction import TransactionStatus, TransactionType
from app.schemas.analytics import UpcomingExpectedAmountResponse
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.services.analytics_service import AnalyticsService
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.get(
    "/expected-in-next-7-days",
    response_model=UpcomingExpectedAmountResponse,
    summary="Calculate expected credit recovery in next 7 days",
)
async def get_expected_receivables_7_days(db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_expected_receivables_7_days(db)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Record transaction")
async def create_transaction(tx_in: TransactionCreate, db: AsyncSession = Depends(get_db)):
    tx = await TransactionService.create_transaction(db, tx_in)
    return TransactionResponse.model_validate(tx)


@router.get("/", response_model=List[TransactionResponse], summary="List transactions")
async def list_transactions(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by type"),
    tx_status: Optional[TransactionStatus] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    transactions = await TransactionService.get_transactions(
        db, customer_id=customer_id, transaction_type=transaction_type, tx_status=tx_status, limit=limit, offset=offset
    )
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionResponse, summary="Get single transaction")
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    tx = await TransactionService.get_transaction_by_id(db, transaction_id)
    return TransactionResponse.model_validate(tx)


@router.put("/{transaction_id}", response_model=TransactionResponse, summary="Update transaction")
async def update_transaction(
    transaction_id: int, tx_in: TransactionUpdate, db: AsyncSession = Depends(get_db)
):
    tx = await TransactionService.update_transaction(db, transaction_id, tx_in)
    return TransactionResponse.model_validate(tx)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, summary="Delete transaction")
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    await TransactionService.delete_transaction(db, transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
