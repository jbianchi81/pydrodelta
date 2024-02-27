from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.procedures.generic_linear_channel import GenericLinearChannelProcedureFunction
from typing import TypedDict

class UHParameters(TypedDict):
    u: list

class UHExtraPars(TypedDict):
    dt: float

class UHLinearChannelProcedureFunction(GenericLinearChannelProcedureFunction):
    """Unit hydrograph linear channel procedure"""

    @property
    def coefficients(self):
        """Linear channel coefficients (u)"""
        return self.parameters["u"]
    
    @property
    def Proc(self):
        """Linear channel procedure"""
        return "UH"

    def __init__(
            self,
            parameters : UHParameters,
            extra_pars : UHExtraPars = dict(),
            **kwargs
        ):
        """
        Unit Hydrograph linear channel

        Keyword Arguments:
        ------------------
        - parameters : UHParameters
        dict with properties: u: distribution function. list of floats 

        - extra_pars: UHExtraPars
        dict with properties: dt: calculation timestep (default=1)

        Examples:
        ---------
        ```
        uh_linear_channel = UHLinearChannelProcedureFunction(
            parameters={"u": [0.2,0.5,0.3]},
            extra_pars:{"dt": 1}
        )
        ```
        """
        super().__init__(
            parameters = parameters, 
            extra_pars = extra_pars, 
            **kwargs)
        getSchemaAndValidate(
            dict(
                kwargs, 
                parameters = parameters, 
                extra_pars = extra_pars),
            "UHLinearChannelProcedureFunction")
