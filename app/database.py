import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import URL
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("TARGET_DATABASE_URL")

db_url = URL.create(
    drivername='postgresql+asyncpg',
    username= 'postgres',
    password= 'Z@)5b#JYzmm3.vN',
    host='localhost',
    port=5432,
    database= 'offers_db'
)

engine = create_async_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)
new_session = async_sessionmaker(engine, autoflush=False, expire_on_commit= False)

async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session