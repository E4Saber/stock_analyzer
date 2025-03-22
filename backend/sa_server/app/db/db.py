from .connection import Database


async def get_db():
    db = Database("postgres://xql:xql123@115.190.73.63/stock_analyzer?sslmode=disable")
    await db.connect()
    return db
