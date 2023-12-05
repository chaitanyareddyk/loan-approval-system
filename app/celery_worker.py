from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from app.db.database import SyncSessionLocal, LoanApplication
from app.config import EnvDetails

app = Celery('celery_worker', broker=EnvDetails.REDIS_URL, backend=EnvDetails.REDIS_URL)
logger = get_task_logger(__name__)


def calculate_monthly_emi(loan_amount, annual_interest_rate, loan_tenure_months):
    monthly_interest_rate = annual_interest_rate / (12 * 100)
    emi = loan_amount * monthly_interest_rate / \
        (1 - (1 + monthly_interest_rate) ** -loan_tenure_months)
    return emi


def calculate_risk_score(application):
    risk_score = 0

    # Assess credit score
    if application.credit_score < 600:
        risk_score += 4
    elif application.credit_score < 700:
        risk_score += 2

    # Assess debt-to-income ratio
    debt_to_income_ratio = application.debt / application.income
    if debt_to_income_ratio > 0.4:
        risk_score += 3

    # Assess employment status
    if application.employment_status != "employed":
        risk_score += 2

    # Assess loan amount
    if application.loan_amount > 20000:
        risk_score += 2

    # Assess loan purpose
    if application.loan_purpose not in ["home", "education"]:
        risk_score += 1

    # Check if total EMIs exceed 80% of monthly income
    new_emi = calculate_monthly_emi(application.loan_amount,
                                    application.interest_rate,
                                    application.loan_tenure)
    total_emi = application.existing_emis + new_emi
    if total_emi > (0.8 * application.income):
        risk_score += 5

    return risk_score


@app.task
def process_loan(application_id):
    logger.info(f"Processing loan application {application_id}")
    with SyncSessionLocal() as session:
        statement = select(LoanApplication).where(LoanApplication.id == application_id)
        result = session.execute(statement)
        application = result.scalar_one_or_none()

        if application is None:
            logger.info(f"Application ID {application_id} not found")
            return {"error": "Application not found"}

        risk_score = calculate_risk_score(application)
        application.status = "Approved" if risk_score <= 7 else "Rejected"

        session.commit()
        logger.info(f"Application ID {application_id} processed with status {application.status}")
        return {"application_id": application_id, "status": application.status}