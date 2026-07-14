from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.config import DATABASE_URL
from src.database.models import Base

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)