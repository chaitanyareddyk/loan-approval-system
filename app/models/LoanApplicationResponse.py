from pydantic import BaseModel, PositiveInt

class LoanApplicationResponse(BaseModel):
    application_id: PositiveInt
    status: str
    message: str
