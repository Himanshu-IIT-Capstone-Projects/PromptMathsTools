# tools/arithmetic_tools.py

from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    print("\n [add()] started")
    try:
        return a + b
    except Exception as error:
        print(f"\n [add()] error: {error!r}")
        raise
    finally:
        print("\n [add()] ended")

@tool
def subtract(a: float, b: float) -> float:
    """Subtracts b from a (a - b)."""
    print("\n [subtract()] started")
    try:
        return a - b
    except Exception as error:
        print(f"\n [subtract()] error: {error!r}")
        raise
    finally:
        print("\n [subtract()] ended")

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    print("\n [multiply()] started")
    try:
        return a * b
    except Exception as error:
        print(f"\n [multiply()] error: {error!r}")
        raise
    finally:
        print("\n [multiply()] ended")

@tool
def divide(a: float, b: float) -> float | str:
    """Divides a by b (a / b)."""
    print("\n [divide()] started")
    try:
        if b == 0:
            return "Error: Cannot divide by zero."
        return a / b
    except Exception as error:
        print(f"\n [divide()] error: {error!r}")
        raise
    finally:
        print("\n [divide()] ended")