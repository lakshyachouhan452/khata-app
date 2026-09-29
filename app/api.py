from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Customer, Transaction, TransactionStatus, TransactionType
from app.schemas import (
    CustomerCreate,
    CustomerDetailResponse,
    CustomerResponse,
    CustomerUpdate,
    OverdueCustomerItem,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    UpcomingExpectedAmountResponse,
)

router = APIRouter()


# ============================================================================
# SPECIALIZED ENDPOINTS (Placed before parameterized paths to prevent collisions)
# ============================================================================

@router.get(
    "/transactions/expected-in-next-7-days",
    response_model=UpcomingExpectedAmountResponse,
    summary="Calculate total amount expected in next 7 days",
    tags=["Specialized Endpoints"],
)
async def get_expected_amount_next_7_days(
    db: AsyncSession = Depends(get_db),
) -> UpcomingExpectedAmountResponse:
    """
    Calculates the total receivables expected within the next 7 days.
    Considers 'gave_credit' transactions where status is pending or overdue,
    and due_date falls within [now, now + 7 days].
    """
    now = datetime.now(timezone.utc)
    seven_days_later = now + timedelta(days=7)

    query = (
        select(Transaction)
        .where(
            Transaction.transaction_type == TransactionType.GAVE_CREDIT,
            Transaction.status.in_([TransactionStatus.PENDING, TransactionStatus.OVERDUE]),
            Transaction.due_date.isnot(None),
            Transaction.due_date >= now,
            Transaction.due_date <= seven_days_later,
        )
        .order_by(Transaction.due_date.asc())
    )

    result = await db.execute(query)
    transactions = list(result.scalars().all())

    total_amount = sum((t.amount for t in transactions), Decimal("0.00"))

    return UpcomingExpectedAmountResponse(
        total_expected_amount=total_amount,
        start_date=now,
        end_date=seven_days_later,
        transaction_count=len(transactions),
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
    )


@router.get(
    "/customers/overdue",
    response_model=List[OverdueCustomerItem],
    summary="Fetch all customers with overdue status",
    tags=["Specialized Endpoints"],
)
async def get_overdue_customers(
    db: AsyncSession = Depends(get_db),
) -> List[OverdueCustomerItem]:
    """
    Fetches all customers who currently have overdue receivables.
    Includes customers with transactions explicitly marked 'overdue',
    or 'pending' transactions whose due_date has already passed.
    """
    now = datetime.now(timezone.utc)

    # Find transactions that are overdue or past due date
    overdue_tx_query = (
        select(Transaction)
        .options(selectinload(Transaction.customer))
        .where(
            Transaction.transaction_type == TransactionType.GAVE_CREDIT,
            or_(
                Transaction.status == TransactionStatus.OVERDUE,
                (
                    (Transaction.status == TransactionStatus.PENDING)
                    & (Transaction.due_date.isnot(None))
                    & (Transaction.due_date < now)
                ),
            ),
        )
        .order_by(Transaction.customer_id)
    )

    result = await db.execute(overdue_tx_query)
    overdue_txs = result.scalars().all()

    # Group by customer
    customers_map: dict[int, dict] = {}
    for tx in overdue_txs:
        c_id = tx.customer_id
        if c_id not in customers_map:
            customers_map[c_id] = {
                "customer": tx.customer,
                "overdue_amount": Decimal("0.00"),
                "overdue_transactions": [],
            }
        customers_map[c_id]["overdue_amount"] += tx.amount
        customers_map[c_id]["overdue_transactions"].append(
            TransactionResponse.model_validate(tx)
        )

    return [
        OverdueCustomerItem(
            customer=CustomerResponse.model_validate(data["customer"]),
            overdue_amount=data["overdue_amount"],
            overdue_transactions=data["overdue_transactions"],
        )
        for data in customers_map.values()
    ]


# ============================================================================
# CUSTOMER CRUD
# ============================================================================

@router.post(
    "/customers/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    tags=["Customers"],
)
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    # Check duplicate phone
    stmt = select(Customer).where(Customer.phone == customer_in.phone)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with phone number '{customer_in.phone}' already exists.",
        )

    customer = Customer(
        name=customer_in.name,
        phone=customer_in.phone,
        total_outstanding=Decimal("0.00"),
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.get(
    "/customers/",
    response_model=List[CustomerResponse],
    summary="List all customers",
    tags=["Customers"],
)
async def list_customers(
    search: Optional[str] = Query(None, description="Filter by customer name or phone"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[CustomerResponse]:
    query = select(Customer).order_by(Customer.id.asc()).offset(offset).limit(limit)
    if search:
        search_filter = f"%{search.strip()}%"
        query = query.where(
            or_(
                Customer.name.ilike(search_filter),
                Customer.phone.ilike(search_filter),
            )
        )

    result = await db.execute(query)
    customers = result.scalars().all()
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerDetailResponse,
    summary="Get customer by ID with transaction history",
    tags=["Customers"],
)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
) -> CustomerDetailResponse:
    query = (
        select(Customer)
        .options(selectinload(Customer.transactions))
        .where(Customer.id == customer_id)
    )
    result = await db.execute(query)
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found.",
        )
    return CustomerDetailResponse.model_validate(customer)


@router.put(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer details",
    tags=["Customers"],
)
async def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
) -> CustomerResponse:
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found.",
        )

    if customer_in.phone and customer_in.phone != customer.phone:
        stmt = select(Customer).where(Customer.phone == customer_in.phone)
        duplicate = (await db.execute(stmt)).scalars().first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone number '{customer_in.phone}' is already registered to another customer.",
            )
        customer.phone = customer_in.phone

    if customer_in.name is not None:
        customer.name = customer_in.name

    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete(
    "/customers/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete customer and associated transactions",
    tags=["Customers"],
)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found.",
        )
    await db.delete(customer)
    await db.commit()


# ============================================================================
# TRANSACTION CRUD
# ============================================================================

@router.post(
    "/transactions/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new transaction",
    tags=["Transactions"],
)
async def create_transaction(
    tx_in: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    customer = await db.get(Customer, tx_in.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {tx_in.customer_id} not found.",
        )

    transaction = Transaction(
        customer_id=tx_in.customer_id,
        amount=tx_in.amount,
        transaction_type=tx_in.transaction_type,
        due_date=tx_in.due_date,
        status=tx_in.status,
    )
    db.add(transaction)

    # Adjust customer's total outstanding balance
    if tx_in.transaction_type == TransactionType.GAVE_CREDIT:
        customer.total_outstanding += tx_in.amount
    elif tx_in.transaction_type == TransactionType.RECEIVED_PAYMENT:
        customer.total_outstanding -= tx_in.amount

    await db.commit()
    await db.refresh(transaction)
    return TransactionResponse.model_validate(transaction)


@router.get(
    "/transactions/",
    response_model=List[TransactionResponse],
    summary="List transactions with filters",
    tags=["Transactions"],
)
async def list_transactions(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    tx_status: Optional[TransactionStatus] = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[TransactionResponse]:
    query = select(Transaction).order_by(Transaction.created_at.desc()).offset(offset).limit(limit)

    if customer_id is not None:
        query = query.where(Transaction.customer_id == customer_id)
    if transaction_type is not None:
        query = query.where(Transaction.transaction_type == transaction_type)
    if tx_status is not None:
        query = query.where(Transaction.status == tx_status)

    result = await db.execute(query)
    transactions = result.scalars().all()
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction by ID",
    tags=["Transactions"],
)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    transaction = await db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found.",
        )
    return TransactionResponse.model_validate(transaction)


@router.put(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update transaction details",
    tags=["Transactions"],
)
async def update_transaction(
    transaction_id: int,
    tx_in: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
) -> TransactionResponse:
    transaction = await db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found.",
        )

    customer = await db.get(Customer, transaction.customer_id)

    # Handle impact on customer's total outstanding if amount or transaction_type is modified
    old_amount = transaction.amount
    old_type = transaction.transaction_type
    new_amount = tx_in.amount if tx_in.amount is not None else old_amount
    new_type = tx_in.transaction_type if tx_in.transaction_type is not None else old_type

    if customer and (new_amount != old_amount or new_type != old_type):
        # Reverse old impact
        if old_type == TransactionType.GAVE_CREDIT:
            customer.total_outstanding -= old_amount
        elif old_type == TransactionType.RECEIVED_PAYMENT:
            customer.total_outstanding += old_amount

        # Apply new impact
        if new_type == TransactionType.GAVE_CREDIT:
            customer.total_outstanding += new_amount
        elif new_type == TransactionType.RECEIVED_PAYMENT:
            customer.total_outstanding -= new_amount

    # Update transaction attributes
    if tx_in.amount is not None:
        transaction.amount = tx_in.amount
    if tx_in.transaction_type is not None:
        transaction.transaction_type = tx_in.transaction_type
    if tx_in.due_date is not None:
        transaction.due_date = tx_in.due_date
    if tx_in.status is not None:
        transaction.status = tx_in.status

    await db.commit()
    await db.refresh(transaction)
    return TransactionResponse.model_validate(transaction)


@router.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
    tags=["Transactions"],
)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    transaction = await db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found.",
        )

    # Reverse impact on customer total_outstanding
    customer = await db.get(Customer, transaction.customer_id)
    if customer:
        if transaction.transaction_type == TransactionType.GAVE_CREDIT:
            customer.total_outstanding -= transaction.amount
        elif transaction.transaction_type == TransactionType.RECEIVED_PAYMENT:
            customer.total_outstanding += transaction.amount

    await db.delete(transaction)
    await db.commit()
