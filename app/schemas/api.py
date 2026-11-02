from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, field_validator
class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
class Login(BaseModel):
    email: EmailStr
    password: str
class TransferRequest(BaseModel):
    source_id: str
    destination_id: str
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
class FundingRequest(BaseModel):
    account_id: str
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
class AccountResponse(BaseModel):
    id: str
    currency: str
    balance: Decimal
    status: str
    model_config = {"from_attributes": True}
