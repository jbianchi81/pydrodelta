from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
from pydrodelta.generic_linear_channel import GenericLinearChannelProcedureFunction
import numpy as np

schemas, resolver = getSchema("LinearChannelProcedureFunction","data/schemas/json")
schema = schemas["LinearChannelProcedureFunction"]

class LinearChannelProcedureFunction(GenericLinearChannelProcedureFunction):
    def __init__(self,params,procedure):
        """
        Nash linear channel (gamma distribution)

        params:
        k: residence time
        n: number of reservoirs
        dt: calculation timestep
        """
        super().__init__(params,procedure)
        validate(params,schema,resolver)
        self.coefficients = np.array([params["k"], params["n"]])
        self.Proc = "Nash"
