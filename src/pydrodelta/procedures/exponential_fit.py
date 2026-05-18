from .linear_fit import LinearFitProcedure
from ..types.procedure_full_init_kwargs import ProcedureFullInitKwargs
from typing_extensions import Unpack

class ExponentialFitProcedure(LinearFitProcedure):
    """Procedure function that fits an exponential function between an independent variable (input) and a response and then applies the resulting function to the input values to produce the output"""

    def __init__(
        self,
        **kwargs : Unpack[ProcedureFullInitKwargs]):
        """
        
        **kwargs : keyword arguments (see LinearFitProcedureFunction)
        """
        super().__init__(**kwargs)
        self.type = "exponential"