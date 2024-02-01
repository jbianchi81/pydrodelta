from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
from pydrodelta.procedures.generic_linear_channel import GenericLinearChannelProcedureFunction
from pydrodelta.model_parameter import ModelParameter
import numpy as np
from typing import Union

schemas, resolver = getSchema("LinearChannelProcedureFunction","data/schemas/json")
schema = schemas["LinearChannelProcedureFunction"]

class LinearChannelProcedureFunction(GenericLinearChannelProcedureFunction):

    _parameters = [
       ModelParameter(name="k", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n", constraints=(1,1,5,8))
    ]

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

    def setParameters(self, parameters: Union[list,tuple] = ...):
        super().setParameters(parameters)
        self.coefficients = np.array([self.parameters["k"], self.parameters["n"]])
