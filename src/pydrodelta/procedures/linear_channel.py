from pydrodelta.procedures import GenericLinearChannelProcedure
from pydrodelta.model_parameter import ModelParameter
from typing import Any, List, TypedDict, Union, Mapping, Optional
from typing_extensions import Unpack
from ..types.procedure_init_kwargs import ProcedureInitKwargs

class LinearChannelExtraParsDict(TypedDict, total=False):
    dt : float
    """calculation timestep"""

class LinearChannelParsDict(TypedDict):
    k : float
    """residence time (model parameter)"""
    n : float
    """number of reservoirs (model parameter)"""

class LinearChannelProcedure(GenericLinearChannelProcedure):
    """Nash Linear channel procedure (gamma distribution)"""

    _parameters = [
       ModelParameter(name="k", constraints=(0.2,0.5,8,25)),
       ModelParameter(name="n", constraints=(1,1,5,8))
    ]
    """Model parameters: k, n"""

    @property
    def coefficients(self):
        """Linear channel coefficients (k, n)"""
        if isinstance(self.parameters, list):
            return [self.parameters[0],self.parameters[1]]
        return [self.parameters["k"], self.parameters["n"]]

    @property
    def Proc(self):
        """Linear channel procedure"""
        return "Nash"    

    def __init__(
        self,
        parameters : Union[List[float], LinearChannelParsDict],
        initial_states: Optional[Union[List[float], Mapping[str, Any]]]=None,
        extra_pars: Optional[LinearChannelExtraParsDict]=None,
        **kwargs : Unpack[ProcedureInitKwargs]
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
        super().__init__(parameters = parameters, initial_states=initial_states if initial_states is not None else [0], extra_pars=extra_pars if extra_pars is not None else {}, **kwargs)
        # getSchemaAndValidate(dict(kwargs,parameters = parameters),"LinearChannelProcedureFunction")
        # self.coefficients = np.array([self.parameters["k"], self.parameters["n"]])
        # self.Proc = "Nash"
        
    # def setParameters(
    #     self, 
    #     parameters: Union[list,tuple] = ...
    #     ) -> None:
    #     super().setParameters(parameters)
    #     # self.coefficients = np.array([self.parameters["k"], self.parameters["n"]])
