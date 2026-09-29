import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.transaction import Transaction, TransactionStatus, TransactionType

logger = logging.getLogger("khata.tasks")


async def check_and_update_overdue_transactions():
    """
    Background job to identify pending credit transactions past their due date
    and mark their status as OVERDUE.
    """
    async with AsyncSessionLocal() as db:
        try:
            now = datetime.now(timezone.utc)
            query = select(Transaction).where(
                Transaction.transaction_type == TransactionType.GAVE_CREDIT,
                Transaction.status == TransactionStatus.PENDING,
                Transaction.due_date.isnot(None),
                Transaction.due_date < now,
            )
            result = await db.execute(query)
            overdue_list = result.scalars().all()

            if overdue_list:
                for tx in overdue_list:
                    tx.status = TransactionStatus.OVERDUE
                await db.commit()
                logger.info(f"Marked {len(overdue_list)} transactions as OVERDUE.")
        except Exception as e:
            logger.error(f"Error in overdue checker job: {e}")
            await db.rollback()


async def periodic_overdue_checker_task(interval_seconds: int = 3600):
    """Periodic loop for background overdue checking."""
    while True:
        await check_and_update_overdue_transactions()
        await asyncio.sleep(interval_seconds)
