from pydrodelta.procedures.linear_combination import LinearCombinationProcedureFunction
from pydrodelta.function_boundary import FunctionBoundary

class LinearCombination4BProcedureFunction(LinearCombinationProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        FunctionBoundary({"name": "input_2", "warmup_only": True}),
        FunctionBoundary({"name": "input_3", "warmup_only": True}),
        FunctionBoundary({"name": "input_4", "warmup_only": True})
    ]

