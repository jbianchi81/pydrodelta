from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
from pydrodelta.procedures.generic_linear_channel import GenericLinearChannelProcedureFunction
import numpy as np

class UHLinearChannelProcedureFunction(GenericLinearChannelProcedureFunction):
    def __init__(
            self,
            **kwargs
        ):
        """
        Unit Hydrograph linear channel

        params:
        u: distribution function. list of floats 
        dt: calculation timestep
        """
        super().__init__(**kwargs)
        getSchemaAndValidate(kwargs,"UHLinearChannelProcedureFunction")
        self.coefficients = np.array(self.parameters["u"])
        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 1
        self.Proc = "UH"
