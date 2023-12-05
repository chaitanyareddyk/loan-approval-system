import pytest
from fastapi.testclient import TestClient
from app.main import app, create_tables
from app.models.LoanApplicationCreate import LoanApplicationCreate
from app.db.database import AsyncSessionLocal

client = TestClient(app)

# test data
test_application_data = {
    "name": "KC Reddy",
    "credit_score": 700,
    "loan_amount": 15000,
    "loan_purpose": "education",
    "income": 6000,
    "employment_status": "employed",
    "debt": 1000,
    "existing_emis": 500,
    "interest_rate": 5,
    "loan_tenure": 12,
}

@pytest.fixture(scope="module")
def database_setup():
    create_tables()

@pytest.fixture(scope="function")
async def database_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
def test_create_application():
    response = client.post("/apply", json=test_application_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "received"

@pytest.fixture
def test_get_application_status():
    response = client.post("/apply", json=test_application_data)
    assert response.status_code == 201
    data = response.json()
    application_id = data["application_id"]

    response = client.get(f"/application/{application_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"

@pytest.fixture
def test_update_application():
    response = client.post("/apply", json=test_application_data)
    assert response.status_code == 201
    data = response.json()
    application_id = data["application_id"]

    updated_data = {
        "loan_amount": 20000.0,
        "loan_purpose": "home",
    }
    response = client.put(f"/application/{application_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Application updated successfully"

@pytest.fixture
def test_delete_application():
    response = client.post("/apply", json=test_application_data)
    assert response.status_code == 201
    data = response.json()
    application_id = data["application_id"]

    response = client.delete(f"/application/{application_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Application deleted successfully"
    
@pytest.fixture
def test_invalid_application_id():
    response = client.get("/application/9999/status")
    assert response.status_code == 404

