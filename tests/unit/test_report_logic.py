import pytest
from unittest.mock import MagicMock, patch
from app.routes.report_routes import compute_report
from app.models import Calculation


def make_calc(op, a, b, result):
    c = MagicMock(spec=Calculation)
    c.operation = op
    c.operand_a = a
    c.operand_b = b
    c.result = result
    return c


def test_empty_report():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    # mock the group-by chain
    db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
    report = compute_report(1, db)
    assert report.total_calculations == 0
    assert report.most_used_operation is None


def test_report_totals(db):
    from tests.conftest import TestingSession
    from app.models import User
    from app.auth import hash_password
    session = TestingSession()
    user = User(username="r", email="r@r.com", hashed_password=hash_password("pass1234"))
    session.add(user)
    session.commit()
    for op, a, b, res in [("add",2,3,5),("add",1,1,2),("multiply",3,3,9)]:
        session.add(Calculation(user_id=user.id, operation=op, operand_a=a, operand_b=b, result=res))
    session.commit()
    report = compute_report(user.id, session)
    assert report.total_calculations == 3
    assert report.most_used_operation == "add"
    assert len(report.operation_breakdown) == 2