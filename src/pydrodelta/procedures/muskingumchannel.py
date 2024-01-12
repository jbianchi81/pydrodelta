from pydrodelta.procedure_function import ProcedureFunction, ProcedureFunctionResults
from pydrodelta.validation import getSchema, validate
from pydrodelta.pydrology import MuskingumChannel
from pandas import DataFrame
from pydrodelta.function_boundary import FunctionBoundary
import logging

schemas, resolver = getSchema("MuskingumChannelProcedureFunction","data/schemas/json")
schema = schemas["MuskingumChannelProcedureFunction"]

class MuskingumChannelProcedureFunction(ProcedureFunction):

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
        self.K = params["K"]
        self.X = params["X"]
        self.Proc = params["Proc"] if "Proc" in params else "Muskingum"
        self.initial_states = params["initial_states"] if "initial_states" in params else [0] # None
        self.engine = None

    def run(self,input=None):
        """input[0]: hidrograma en borde superior del tramo (DataFrame con index:timestamp y valor:float)"""
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        # logging.debug(input)
        # if self.initial_states is None:
        #     self.initial_states = [input[0].dropna().valor[0], input[1].dropna().valor[0]]
        self.engine = MuskingumChannel([self.K, self.X], input[0]["valor"].to_list(),self.initial_states,self.Proc)
        self.engine.computeOutFlow()
        data = DataFrame({"valor": self.engine.Outflow},index=input[0].index)
        data_ = data[["valor"]].rename(columns={"valor":"output"}).join(input[0][["valor"]].rename(columns={"valor":"input"}))
        return (
            [data], 
            ProcedureFunctionResults({
                "data": data_
            })
        )