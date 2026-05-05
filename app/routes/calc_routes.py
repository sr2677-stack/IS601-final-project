from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Calculation
from app.schemas import CalcCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def perform_calculation(op: str, a: float, b: float) -> float:
    """Pure function — easy to unit test."""
    match op:
        case "add":      return a + b
        case "subtract": return a - b
        case "multiply": return a * b
        case "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        case "power":    return a ** b
        case "modulus":
            if b == 0:
                raise ValueError("Modulus by zero")
            return a % b
        case _:
            raise ValueError(f"Unknown operation: {op}")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    calcs = db.query(Calculation).filter(Calculation.user_id == current_user.id).order_by(Calculation.created_at.desc()).limit(5).all()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "user": current_user, "recent": calcs},
    )


@router.post("/calculate")
def calculate(
    operation: str = Form(...),
    operand_a: float = Form(...),
    operand_b: float = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        schema = CalcCreate(operation=operation, operand_a=operand_a, operand_b=operand_b)
        result = perform_calculation(schema.operation, schema.operand_a, schema.operand_b)
    except PydanticValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    calc = Calculation(
        user_id=current_user.id,
        operation=schema.operation,
        operand_a=schema.operand_a,
        operand_b=schema.operand_b,
        result=result,
    )
    db.add(calc)
    db.commit()
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/calculations/{calc_id}/delete")
def delete_calculation(calc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id, Calculation.user_id == current_user.id).first()
    if calc:
        db.delete(calc)
        db.commit()
    return RedirectResponse("/history", status_code=303)
