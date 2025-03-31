import asyncio
from app.db.db import get_db
from .db_services.stock_service.stock_basic.stock_basic_service import import_single_stock
from .db_services.stock_service.stock_basic.stk_premarket_service import import_single_premarket
from .db_services.stock_service.stock_basic.tarde_cal_service import import_exchange_calendar
from .db_services.stock_service.stock_basic.namechange_service import import_stock_namechange
from .db_services.stock_service.stock_basic.hs_const_service import import_sh_connect
from .db_services.stock_service.stock_basic.stock_company_service import import_single_company
from .db_services.stock_service.stock_basic.stk_managers_service import import_stock_managers
from .db_services.stock_service.stock_basic.stk_rewards_service import import_stock_rewards
from .db_services.stock_service.stock_basic.new_share_service import get_annual_ipo_stats
from .db_services.stock_service.stock_basic.bak_basic_service import get_market_overview
from .db_services.stock_service.fund_flows.moneyflow_service import import_daily_moneyflow
from .db_services.stock_service.stock_financial.income_service import import_income_with_params
from .db_services.stock_service.stock_financial.balancesheet_service import import_stock_balancesheet
from .db_services.stock_service.stock_financial.cashflow_service import import_stock_cashflow
from .db_services.stock_service.stock_financial.forecast_service import import_stock_forecast
from .db_services.stock_service.stock_financial.express_service import import_stock_express


async def stock_basic_test():
    db = await get_db()
    try:
        await import_single_stock(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def stk_premarket_test():
    db = await get_db()
    try:
        await import_single_premarket(db, trade_date='20210930', ts_code='000001.SZ')
    finally:
        await db.close()

async def trade_cal_test():
    db = await get_db()
    try:
        await import_exchange_calendar(db, exchange='SSE', start_date='20210101', end_date='20210102')
    finally:
        await db.close()

async def namechange_test():
    db = await get_db()
    try:
        await import_stock_namechange(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def hs_const_test():
    db = await get_db()
    try:
        await import_sh_connect(db, is_new='1')
    finally:
        await db.close()

async def stock_company_test():
    db = await get_db()
    try:
        await import_single_company(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def stk_managers_test():
    db = await get_db()
    try:
        await import_stock_managers(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def stk_rewards_test():
    db = await get_db()
    try:
        await import_stock_rewards(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def new_share_test():
    db = await get_db()
    try:
        await get_annual_ipo_stats(db, year=2021)
    finally:
        await db.close()

async def bak_basic_test():
    db = await get_db()
    try:
        await get_market_overview(db, trade_date='20250317')
    finally:
        await db.close()

async def moneyflow_test():
    db = await get_db()
    try:
        await import_daily_moneyflow(db, trade_date='20210930')
    finally:
        await db.close()

async def income_test():
    db = await get_db()
    try:
        await import_income_with_params(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def balancesheet_test():
    db = await get_db()
    try:
        await import_stock_balancesheet(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def cashflow_test():
    db = await get_db()
    try:
        await import_stock_cashflow(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def forecast_test():
    db = await get_db()
    try:
        await import_stock_forecast(db, ts_code='000001.SZ')
    finally:
        await db.close()

async def express_test():
    db = await get_db()
    try:
        await import_stock_express(db, ts_code='000001.SZ')
    finally:
        await db.close()

if __name__ == "__main__":
    # asyncio.run(stock_basic_test())
    # asyncio.run(stk_premarket_test())
    # asyncio.run(trade_cal_test())
    # asyncio.run(namechange_test())
    # asyncio.run(hs_const_test())
    # asyncio.run(stock_company_test())
    # asyncio.run(stk_managers_test())
    # asyncio.run(stk_rewards_test())
    # asyncio.run(new_share_test())
    # asyncio.run(bak_basic_test())
    # asyncio.run(moneyflow_test())
    # asyncio.run(income_test())
    # asyncio.run(balancesheet_test())
    # asyncio.run(cashflow_test())
    # asyncio.run(forecast_test())
    asyncio.run(express_test())