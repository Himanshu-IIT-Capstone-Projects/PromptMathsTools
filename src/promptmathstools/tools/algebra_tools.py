# tools/algebra_tools.py
import sympy as sp
from langchain_core.tools import tool

@tool
def solve_quadratic(equation_str: str) -> str:
    """Solves algebraic or quadratic equations equal to 0 for x (e.g., '(x + 2)*(x - 3)')."""
    print("\n [solve_quadratic()] started")
    try:
        x = sp.Symbol("x")
        roots = sp.solve(sp.sympify(equation_str), x)
        return f"Roots for x: {roots}"
    except Exception as e:
        print(f"\n [solve_quadratic()] error: {e!r}")
        return f"Equation parsing error: {e}"
    finally:
        print("\n [solve_quadratic()] ended")
