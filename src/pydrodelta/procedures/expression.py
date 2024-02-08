from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.function_boundary import FunctionBoundary

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
    def __init__(
        self,
        expression : str,
        **kwargs):
        """
        Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
        Guarda procedure en self._procedure (procedimiento al cual pertenece la función)
        
        Parameters:
        -----------
        expression :str
            Expression to evaluate. For each step of input, 'value' is replaced with the value of input and the expression is evaluated
        \**kwargs : keyword arguments"""
        super().__init__(**kwargs)
        getSchemaAndValidate(kwargs,"ExpressionProcedureFunction")
        self.expression = expression
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