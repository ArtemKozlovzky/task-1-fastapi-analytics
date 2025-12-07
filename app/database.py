import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import URL
from dotenv import load_dotenv

load_dotenv()

db_url = URL.create(
    drivername='postgresql+asyncpg',
    username= os.getenv('TARGET_USER'),
    password= os.getenv('TARGET_PASSWORD'),
    host= os.getenv('TARGET_HOST'),
    port=5432,
    database= os.getenv('TARGET_DBNAME')
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