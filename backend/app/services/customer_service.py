from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    @staticmethod
    async def create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
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
        return customer

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Customer]:
        query = select(Customer).order_by(Customer.id.asc()).offset(offset).limit(limit)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Customer.name.ilike(pattern),
                    Customer.phone.ilike(pattern),
                )
            )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Customer:
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
        return customer

    @staticmethod
    async def update_customer(
        db: AsyncSession, customer_id: int, customer_in: CustomerUpdate
    ) -> Customer:
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
                    detail=f"Phone number '{customer_in.phone}' is already registered.",
                )
            customer.phone = customer_in.phone

        if customer_in.name is not None:
            customer.name = customer_in.name

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: int) -> None:
        customer = await db.get(Customer, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )
        await db.delete(customer)
        await db.commit()
