from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Calculation, User
from app.schemas import OperationStat, ReportOut

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def compute_report(user_id: int, db: Session) -> ReportOut:
    """Pure business logic — no HTTP concerns, fully unit-testable."""
    calcs = db.query(Calculation).filter(Calculation.user_id == user_id).all()

    if not calcs:
        return ReportOut(
            total_calculations=0,
            average_result=0.0,
            most_used_operation=None,
            operation_breakdown=[],
        )

    total = len(calcs)
    avg_result = sum(c.result for c in calcs) / total

    # Group by operation
    breakdown_rows = (
        db.query(
            Calculation.operation,
            func.count(Calculation.id).label("count"),
            func.avg(Calculation.result).label("avg_result"),
        )
        .filter(Calculation.user_id == user_id)
        .group_by(Calculation.operation)
        .all()
    )

    breakdown = [
        OperationStat(operation=r.operation, count=r.count, avg_result=round(r.avg_result, 4))
        for r in breakdown_rows
    ]
    most_used = max(breakdown, key=lambda s: s.count).operation if breakdown else None

    return ReportOut(
        total_calculations=total,
        average_result=round(avg_result, 4),
        most_used_operation=most_used,
        operation_breakdown=breakdown,
    )


@router.get("/history", response_class=HTMLResponse)
def history_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    calcs = (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.id)
        .order_by(Calculation.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"request": request, "user": current_user, "calculations": calcs},
    )


@router.get("/report", response_class=HTMLResponse)
def report_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = compute_report(current_user.id, db)
    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={"request": request, "user": current_user, "report": report},
    )


@router.get("/api/report", response_model=ReportOut)
def report_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """JSON endpoint for the report — useful for integration tests."""
    return compute_report(current_user.id, db)
