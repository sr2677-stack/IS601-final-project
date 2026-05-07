from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ──────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_length(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.strip()


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        return v


# ── Calculations ──────────────────────────────────────
ALLOWED_OPS = {"add", "subtract", "multiply", "divide", "power", "modulus"}


class CalcCreate(BaseModel):
    operation: str
    operand_a: float
    operand_b: float

    @field_validator("operation")
    @classmethod
    def valid_op(cls, v: str) -> str:
        if v not in ALLOWED_OPS:
            raise ValueError(f"operation must be one of {ALLOWED_OPS}")
        return v


class CalcOut(BaseModel):
    id: int
    operation: str
    operand_a: float
    operand_b: float
    result: float
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Reports ───────────────────────────────────────────
class OperationStat(BaseModel):
    operation: str
    count: int
    avg_result: float


class ReportOut(BaseModel):
    total_calculations: int
    average_result: float
    most_used_operation: str | None
    operation_breakdown: list[OperationStat]
