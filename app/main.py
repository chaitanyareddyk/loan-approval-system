from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import AsyncSessionLocal, create_tables, LoanApplication
from prometheus_fastapi_instrumentator import Instrumentator
import logging
from app.celery_worker import process_loan
from app.models.LoanApplicationResponse import LoanApplicationResponse
from app.models.LoanApplicationCreate import LoanApplicationCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def startup_event():
    logger.info("Starting up...")
    await create_tables()
app.add_event_handler("startup", startup_event)


@app.post("/apply", response_model=LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_loan(application_data: LoanApplicationCreate, db: AsyncSession = Depends(get_db)):
    db_application = LoanApplication(**application_data.model_dump())
    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)

    process_loan.delay(db_application.id)
    print("db_application.id", db_application.id)

    logger.info(f"Received loan application from {db_application.name}")
    return LoanApplicationResponse(
        application_id=db_application.id,
        status="received",
        message="Your application has been received and is being processed"
    )

@app.put("/application/{application_id}", status_code=status.HTTP_200_OK)
async def update_application(application_id: int, updated_application: LoanApplicationCreate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        statement = select(LoanApplication).where(LoanApplication.id == application_id)
        result = await session.execute(statement)
        application = result.scalar_one_or_none()

        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")

        for var, value in vars(updated_application).items():
            setattr(application, var, value) if value is not None else None

        await session.commit()
        return {"message": "Application updated successfully", "application_id": application.id}

@app.delete("/application/{application_id}", status_code=status.HTTP_200_OK)
async def delete_application(application_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        statement = select(LoanApplication).where(LoanApplication.id == application_id)
        result = await session.execute(statement)
        application = result.scalar_one_or_none()

        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")

        await session.delete(application)
        await session.commit()
        return {"message": "Application deleted successfully", "application_id": application_id}

@app.get("/application/{application_id}/status", status_code=status.HTTP_200_OK)
async def get_application_status(application_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        statement = select(LoanApplication).where(LoanApplication.id == application_id)
        result = await session.execute(statement)
        application = result.scalar_one_or_none()

        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")

        return {"application_id": application.id, "status": application.status}
