from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

RoleType = Literal["employee", "manager", "finance_admin"]
ExpenseCategory = Literal["Travel","Meals","Accommodation","Office Supplies","Client Entertainment","Other"]
ExpenseStatus = Literal["draft","submitted","approved","rejected","paid"]

class LoginRequest(BaseModel):
    email: EmailStr
    role: RoleType

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    category: ExpenseCategory
    amount: float = Field(..., gt=0)
    expense_date: date
    receipt_filename: Optional[str] = None
    description: Optional[str] = None

class ExpenseUpdate(ExpenseCreate):
    pass

class RejectRequest(BaseModel):
    comment: str = Field(..., min_length=2)

class ExpenseResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    department: Optional[str] = None
    title: str
    category: ExpenseCategory
    amount: float
    expense_date: date
    receipt_filename: Optional[str]
    description: Optional[str]
    status: ExpenseStatus
    submitted_at: Optional[datetime]
    created_at: datetime
