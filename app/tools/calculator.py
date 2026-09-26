import math
from typing import Dict, Any

class CalculationTool:
    @staticmethod
    def evaluate_expression(expr: str) -> Dict[str, Any]:
        """Safely evaluates mathematical expressions for engineering and financial calculations."""
        # Restricted safe globals for math
        safe_dict = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "exp": math.exp
        }
        
        try:
            # Clean string
            clean_expr = expr.replace("^", "**")
            result = eval(clean_expr, {"__builtins__": None}, safe_dict)
            return {
                "expression": expr,
                "result": result,
                "status": "SUCCESS"
            }
        except Exception as e:
            return {
                "expression": expr,
                "error": f"Evaluation error: {str(e)}",
                "status": "FAILED"
            }
