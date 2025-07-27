# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import DATABASE_URL
from app.core.logging.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

sync_engine = async_engine.sync_engine
SessionLocalSync = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def get_sync_db():
    # Synchronous DB session for legacy query usage.
    db = SessionLocalSync()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
