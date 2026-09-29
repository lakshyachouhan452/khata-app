from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.analytics import OverdueCustomerItem
from app.schemas.customer import (
    CustomerCreate,
    CustomerDetailResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.analytics_service import AnalyticsService
from app.services.customer_service import CustomerService

router = APIRouter()


@router.get("/overdue", response_model=List[OverdueCustomerItem], summary="Fetch customers with overdue balance")
async def get_overdue_customers(db: AsyncSession = Depends(get_db)):
    return await AnalyticsService.get_overdue_customers(db)


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, summary="Create customer")
async def create_customer(customer_in: CustomerCreate, db: AsyncSession = Depends(get_db)):
    customer = await CustomerService.create_customer(db, customer_in)
    return CustomerResponse.model_validate(customer)


@router.get("/", response_model=List[CustomerResponse], summary="List customers")
async def list_customers(
    search: Optional[str] = Query(None, description="Search by name or phone"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    customers = await CustomerService.get_customers(db, search=search, limit=limit, offset=offset)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/{customer_id}", response_model=CustomerDetailResponse, summary="Get customer detail with transactions")
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    return CustomerDetailResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse, summary="Update customer")
async def update_customer(
    customer_id: int, customer_in: CustomerUpdate, db: AsyncSession = Depends(get_db)
):
    customer = await CustomerService.update_customer(db, customer_id, customer_in)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete customer")
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    await CustomerService.delete_customer(db, customer_id)
