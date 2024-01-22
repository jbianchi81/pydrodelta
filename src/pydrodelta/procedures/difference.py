from pydrodelta.procedures.junction import JunctionProcedureFunction
from pydrodelta.function_boundary import FunctionBoundary

class DifferenceProcedureFunction(JunctionProcedureFunction):

    _boundaries = [
        FunctionBoundary({"name": "input_1", "warmup_only": True}),
        FunctionBoundary({"name": "input_2", "warmup_only": True})
    ]
    def run(self,input=None):
        return self.runJunction(input=input,substract=True)
