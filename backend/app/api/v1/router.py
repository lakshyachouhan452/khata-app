from fastapi import APIRouter

from app.api.v1.endpoints import customers, transactions

api_v1_router = APIRouter()

api_v1_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_v1_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
