from pydantic import BaseModel, PositiveInt

class LoanApplicationCreate(BaseModel):
    name: str
    credit_score: PositiveInt
    loan_amount: float
    loan_purpose: str
    income: float
    employment_status: str
    debt: float 
    existing_emis: float 
    interest_rate: float
    loan_tenure: PositiveInt