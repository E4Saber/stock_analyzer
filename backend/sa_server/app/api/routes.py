# app/api/routes.py
from fastapi import APIRouter
from app.api.endpoints import stock, market, db_api

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(
    market.router,
    prefix="/market",
    tags=["market"],
)

api_router.include_router(
    stock.router,
    prefix="/stocks",
    tags=["stocks"],
)

api_router.include_router(
    db_api.router,
    prefix="/db_api",
    tags=["db_api"],
)