from unittest.mock import patch
import pytest
from app.celery_worker import process_loan

class MockLoanApplication:
    id = 1
    name = "Chaitanya Reddy"
    credit_score = 750
    loan_amount = 10000
    loan_purpose = "home"
    income = 80000
    employment_status = "employed"
    debt = 5000
    existing_emis = 1000
    interest_rate = 6
    loan_tenure = 10
    status = "pending"

@pytest.fixture
def mock_loan_application():
    return MockLoanApplication()

@patch('app.db.database.SyncSessionLocal')
def test_process_loan_positive(mock_session, mock_loan_application):
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_loan_application

    result = process_loan(1)

    assert result == {"application_id": 1, "status": "Approved"}
    assert mock_loan_application.status == "pending"
