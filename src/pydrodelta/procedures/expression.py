from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
import math

class ExpressionProcedureFunction(ProcedureFunction):
    """Procedure function that evaluates an arbitrary expression where 'value' is replaced with the values of input"""
    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]
    """Only one input allowed"""
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    """Only one output allowed"""

    @property
    def allow_na(self) -> bool:
        """allow for null values in input. Defaults to False"""
        return self.extra_pars["allow_na"] if "allow_na" in self.extra_pars else False

    def __init__(
        self,
        expression : str,
        **kwargs):
        """
        expression :str

            Expression to evaluate. For each step of input, 'value' is replaced with the value of input and the expression is evaluated
        
        \**kwargs : keyword arguments (see ProcedureFunction)
        """
        super().__init__(**kwargs)
        getSchemaAndValidate(
            dict(
                kwargs, 
                expression = expression),
            "ExpressionProcedureFunction")
        self.expression = expression
        if self.allow_na:
            self.boundaries[0].optional = True

    def transformation_function(
        self,
        value : float
        ) -> float:
        """Evaluates self.expression replacing 'value' with value
        
        Parameters:
        -----------
        value : float
            The value to use in the expression
            
        Returns:
        --------
        float"""
        if value is None:
            return None
        result = eval(self.expression)
        return result
    def run(
        self,
        input : list = None
        ) -> tuple:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        
        Parameters:
        -----------
        input : list of DataFrames
            Procedure function input (boundary conditions). If None, loads using .loadInput()

        Returns:
        --------
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        output  = []
        for serie in input:
            output_serie = serie.copy()
            output_serie.valor = [self.transformation_function(valor) for valor in output_serie.valor]
            output.append(output_serie)
        return (
            output, 
            ProcedureFunctionResults()
        )