from .linear_fit import LinearFitProcedureFunction

class ExponentialFitProcedureFunction(LinearFitProcedureFunction):
    """Procedure function that fits an exponential function between an independent variable (input) and a response and then applies the resulting function to the input values to produce the output"""

    def __init__(
        self,
        **kwargs):
        """
        
        \**kwargs : keyword arguments (see LinearFitProcedureFunction)
        """
        super().__init__(**kwargs)
        self.type = "exponential"