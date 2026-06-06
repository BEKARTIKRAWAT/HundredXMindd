import math
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    allowed_names["__builtins__"] = None
    try:
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
