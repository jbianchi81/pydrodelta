from pydrodelta.procedures.linear_combination import LinearCombinationProcedureFunction
from pydrodelta.function_boundary import FunctionBoundary

class LinearCombination3BProcedureFunction(LinearCombinationProcedureFunction):
    """Linear combination procedure with 3 inputs"""
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        FunctionBoundary({"name": "input_2", "warmup_only": True}),
        FunctionBoundary({"name": "input_3", "warmup_only": True})
    ]

