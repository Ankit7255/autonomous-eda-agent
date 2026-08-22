import sys
import io
import traceback
import pandas as pd
import numpy as np
from typing import Dict

def execute_generated_code(code: str, dataset_path: str) -> Dict[str, str]:
    """
    Executes AI-generated Python code in a restricted local environment.
    Captures stdout for reporting and tracebacks for self-correction.
    """
    captured_output = io.StringIO()
    
    # We add __import__ so the LLM can pull in matplotlib/seaborn autonomously
    restricted_globals = {
        "__builtins__": {
            "print": print, "range": range, "len": len, 
            "int": int, "float": float, "str": str, 
            "list": list, "dict": dict, "Exception": Exception,
            "__import__": __import__,
            "abs": abs, "round": round, "max": max, "min": min, "sum": sum
        },
        "pd": pd,
        "np": np,
    }

    try:
        sys.stdout = captured_output
        exec(code, restricted_globals, {})
        sys.stdout = sys.__stdout__
        return {"output": captured_output.getvalue(), "error": None}
        
    except Exception as e:
        sys.stdout = sys.__stdout__
        error_trace = traceback.format_exc()
        return {"output": captured_output.getvalue(), "error": error_trace}