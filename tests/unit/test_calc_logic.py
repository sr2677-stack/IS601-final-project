import pytest
from app.routes.calc_routes import perform_calculation


def test_add():       assert perform_calculation("add", 3, 4) == 7
def test_subtract():  assert perform_calculation("subtract", 10, 3) == 7
def test_multiply():  assert perform_calculation("multiply", 3, 4) == 12
def test_divide():    assert perform_calculation("divide", 10, 2) == 5
def test_power():     assert perform_calculation("power", 2, 10) == 1024
def test_modulus():   assert perform_calculation("modulus", 10, 3) == 1

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Division by zero"):
        perform_calculation("divide", 5, 0)

def test_modulus_by_zero():
    with pytest.raises(ValueError, match="Modulus by zero"):
        perform_calculation("modulus", 5, 0)

def test_unknown_operation():
    with pytest.raises(ValueError):
        perform_calculation("sqrt", 4, 0)