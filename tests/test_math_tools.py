# tests/test_math_tools.py
from promptmathstools.tools.arithmetic_tools import add, subtract, multiply, divide
from promptmathstools.tools.algebra_tools import solve_quadratic

def test_arithmetic_operations():
    assert add.invoke({"a": 3, "b": 2}) == 5
    assert subtract.invoke({"a": 100, "b": 50}) == 50
    assert multiply.invoke({"a": 100, "b": 0.5}) == 50.0
    assert divide.invoke({"a": 1000, "b": 10}) == 100.0

def test_divide_by_zero():
    result = divide.invoke({"a": 10, "b": 0})
    assert "Error" in str(result)

def test_solve_quadratic():
    result = solve_quadratic.invoke({"equation_str": "(x + 2)*(x - 3)"})
    assert "-2" in result and "3" in result

def test_apple_word_problem_tool_chain():
    price_per_kg = divide.invoke({"a": 1000, "b": 10})
    cost_500g = multiply.invoke({"a": price_per_kg, "b": 0.5})
    balance = subtract.invoke({"a": 100, "b": cost_500g})
    assert balance == 50.0
