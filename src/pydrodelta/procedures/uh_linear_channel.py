from pydrodelta.procedures.generic_linear_channel import GenericLinearChannelProcedure
from typing import TypedDict, Optional
from typing_extensions import Unpack
from ..types.procedure_init_kwargs import ProcedureInitKwargs

class UHParameters(TypedDict):
    u: list

class UHExtraPars(TypedDict):
    dt: Optional[float]

class UHLinearChannelProcedure(GenericLinearChannelProcedure):
    """
    Unit Hydrograph linear channel procedure

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
    """

    @property
    def coefficients(self):
        """Linear channel coefficients (u)"""
        if isinstance(self.parameters, list):
            return self.parameters[0]
        else:
            return self.parameters["u"]
    
    @property
    def Proc(self):
        """Linear channel procedure"""
        return "UH"

    def __init__(
            self,
            parameters : UHParameters,
            extra_pars : UHExtraPars = {"dt": 1},
            **kwargs : Unpack[ProcedureInitKwargs]
        ):
        """
        Unit Hydrograph linear channel procedure

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
        """

        super().__init__(
            parameters = parameters, 
            extra_pars = extra_pars, 
            **kwargs)
        # getSchemaAndValidate(
        #     dict(
        #         kwargs, 
        #         parameters = parameters, 
        #         extra_pars = extra_pars),
        #     "UHLinearChannelProcedure")
