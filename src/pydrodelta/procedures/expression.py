from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary

schemas, resolver = getSchema("ExpressionProcedureFunction","data/schemas/json")
schema = schemas["ExpressionProcedureFunction"]

class ExpressionProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input"})
    ]
    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    def __init__(self,params,procedure):
        """
        Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
        Guarda procedure en self._procedure (procedimiento al cual pertenece la función)
        """
        super().__init__(params,procedure)
        validate(params,schema,resolver)
        self.expression = params["expression"]
    def transformation_function(self,value:float):
        if value is None:
            return None
        result = eval(self.expression)
        return result
    def run(self,input=None):
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
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