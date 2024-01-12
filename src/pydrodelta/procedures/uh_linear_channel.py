from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
from pydrodelta.procedures.generic_linear_channel import GenericLinearChannelProcedureFunction
import numpy as np

schemas, resolver = getSchema("UHLinearChannelProcedureFunction","data/schemas/json")
schema = schemas["UHLinearChannelProcedureFunction"]

class UHLinearChannelProcedureFunction(GenericLinearChannelProcedureFunction):
    def __init__(self,params,procedure):
        """
        Unit Hydrograph linear channel

        params:
        u: distribution function. list of floats 
        dt: calculation timestep
        """
        super().__init__(params,procedure)
        validate(params,schema,resolver)
        self.coefficients = np.array(params["u"])
        self.dt = params["dt"] if "dt" in params else 1
        self.Proc = "UH"
