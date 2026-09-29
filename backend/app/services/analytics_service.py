from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.schemas.analytics import OverdueCustomerItem, UpcomingExpectedAmountResponse
from app.schemas.customer import CustomerResponse
from app.schemas.transaction import TransactionResponse


class AnalyticsService:
    @staticmethod
    async def get_expected_receivables_7_days(
        db: AsyncSession,
    ) -> UpcomingExpectedAmountResponse:
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

    @staticmethod
    async def get_overdue_customers(db: AsyncSession) -> List[OverdueCustomerItem]:
        now = datetime.now(timezone.utc)

        query = (
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

        result = await db.execute(query)
        overdue_txs = result.scalars().all()

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
