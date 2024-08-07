from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.function_boundary import FunctionBoundary
from pydrodelta.pydrology import LinearChannel
from pydrodelta.procedures.generic_linear_channel import GenericLinearChannelProcedureFunction
from pydrodelta.model_parameter import ModelParameter
import numpy as np
from typing import Union

class LinearChannelProcedureFunction(GenericLinearChannelProcedureFunction):
    """Nash Linear channel procedure (gamma distribution)"""

    _parameters = [
       ModelParameter(name="k", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n", constraints=(1,1,5,8))
    ]
    """Model parameters: k, n"""

    @property
    def coefficients(self):
        """Linear channel coefficients (k, n)"""
        return [self.parameters["k"], self.parameters["n"]]

    @property
    def Proc(self):
        """Linear channel procedure"""
        return "Nash"    

    def __init__(
        self,
        parameters : Union[dict,list,tuple],
        **kwargs
        ):
        """
        Nash linear channel (gamma distribution)

        Parameters:
        -----------
        parameters : dict

            properties:
            k : float residence time
            n : float number of reservoirs
        
        /**kwargs : keyword arguments

        Keyword arguments:
        ------------------
        extra_pars: dict
            properties
            dt : float calculation timestep
        """
        super().__init__(parameters = parameters, **kwargs)
        getSchemaAndValidate(dict(kwargs,parameters = parameters),"LinearChannelProcedureFunction")
        # self.coefficients = np.array([self.parameters["k"], self.parameters["n"]])
        # self.Proc = "Nash"
        
    # def setParameters(
    #     self, 
    #     parameters: Union[list,tuple] = ...
    #     ) -> None:
    #     super().setParameters(parameters)
    #     # self.coefficients = np.array([self.parameters["k"], self.parameters["n"]])
