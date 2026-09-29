from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    @staticmethod
    async def create_transaction(db: AsyncSession, tx_in: TransactionCreate) -> Transaction:
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

        # Update customer ledger total outstanding balance
        if tx_in.transaction_type == TransactionType.GAVE_CREDIT:
            customer.total_outstanding += tx_in.amount
        elif tx_in.transaction_type == TransactionType.RECEIVED_PAYMENT:
            customer.total_outstanding -= tx_in.amount

        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        customer_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        tx_status: Optional[TransactionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Transaction]:
        query = select(Transaction).order_by(Transaction.created_at.desc()).offset(offset).limit(limit)

        if customer_id is not None:
            query = query.where(Transaction.customer_id == customer_id)
        if transaction_type is not None:
            query = query.where(Transaction.transaction_type == transaction_type)
        if tx_status is not None:
            query = query.where(Transaction.status == tx_status)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_transaction_by_id(db: AsyncSession, transaction_id: int) -> Transaction:
        tx = await db.get(Transaction, transaction_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found.",
            )
        return tx

    @staticmethod
    async def update_transaction(
        db: AsyncSession, transaction_id: int, tx_in: TransactionUpdate
    ) -> Transaction:
        transaction = await db.get(Transaction, transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found.",
            )

        customer = await db.get(Customer, transaction.customer_id)

        old_amount = transaction.amount
        old_type = transaction.transaction_type
        new_amount = tx_in.amount if tx_in.amount is not None else old_amount
        new_type = tx_in.transaction_type if tx_in.transaction_type is not None else old_type

        # Recalculate customer total outstanding if amount or type modified
        if customer and (new_amount != old_amount or new_type != old_type):
            if old_type == TransactionType.GAVE_CREDIT:
                customer.total_outstanding -= old_amount
            elif old_type == TransactionType.RECEIVED_PAYMENT:
                customer.total_outstanding += old_amount

            if new_type == TransactionType.GAVE_CREDIT:
                customer.total_outstanding += new_amount
            elif new_type == TransactionType.RECEIVED_PAYMENT:
                customer.total_outstanding -= new_amount

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
        return transaction

    @staticmethod
    async def delete_transaction(db: AsyncSession, transaction_id: int) -> None:
        transaction = await db.get(Transaction, transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found.",
            )

        customer = await db.get(Customer, transaction.customer_id)
        if customer:
            if transaction.transaction_type == TransactionType.GAVE_CREDIT:
                customer.total_outstanding -= transaction.amount
            elif transaction.transaction_type == TransactionType.RECEIVED_PAYMENT:
                customer.total_outstanding += transaction.amount

        await db.delete(transaction)
        await db.commit()
