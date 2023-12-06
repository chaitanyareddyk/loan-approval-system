from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.config import EnvDetails


DATABASE_URL = f"postgresql+asyncpg://{EnvDetails.DATABASE_USER}:{EnvDetails.DATABASE_PASSWORD}@{EnvDetails.DATABASE_HOST}:{EnvDetails.DATABASE_PORT}/{EnvDetails.DATABASE_NAME}"
DATABASE_URL_SYNC = f"postgresql://{EnvDetails.DATABASE_USER}:{EnvDetails.DATABASE_PASSWORD}@{EnvDetails.DATABASE_HOST}:{EnvDetails.DATABASE_PORT}/{EnvDetails.DATABASE_NAME}"

async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

sync_engine = create_engine(DATABASE_URL_SYNC, echo=True)
SyncSessionLocal = sessionmaker(bind=sync_engine)

Base = declarative_base()



class LoanApplication(Base):
    __tablename__ = "loan_applications"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    credit_score = Column(Integer)
    loan_amount = Column(Float)
    loan_purpose = Column(String)
    income = Column(Float)
    employment_status = Column(String)
    debt = Column(Float)  # Total debt for debt-to-income ratio calculation
    existing_emis = Column(Float)  # Total amount of existing EMIs
    interest_rate = Column(Float)  # Annual interest rate of the loan
    loan_tenure = Column(Integer)  # Loan tenure in months
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())



async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
