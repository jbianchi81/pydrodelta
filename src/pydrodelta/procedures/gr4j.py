import logging
# from numpy import tanh
# from typing import Optional
# from pydrodelta.series_data import SeriesData
import numpy as np
from pandas import DataFrame, Series, concat

from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.procedures.grp import GRPProcedureFunction
from pydrodelta.pydrology import GR4J

class GR4JProcedureFunction(GRPProcedureFunction):
    # def __init__(self,params,procedure):
    #     """
    #     Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
    #     Guarda procedure en self._procedure (procedimiento al cual pertenece la función)
    #     """
    #     super(GRPProcedureFunction,self).__init__(params,procedure)
    def run(self,input=None) -> tuple:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        boundaries = [ ( input[0]["valor"][i], input[1]["valor"][i]) for i in range(len(input[0])) ]
        self.engine = GR4J(pars=[self.X0,self.X3,self.X2,self.X1],Boundaries=np.array(boundaries),InitialConditions=[self.Sk_init,self.Rk_init])
        self.engine.executeRun()
        q = [x / 1000 / 24 / 60 / 60 / self.dt * self.area * self.ae for x in self.engine.Q][0:len(input[0].index)]
        smc = [x / self.engine.prodStoreMaxStorage * (self.rho - self.wp) + self.wp for x in self.engine.prodStore.SoilStorage][0:len(input[0].index)]
        data = DataFrame({"valor": q},index=input[0].index)
        smcdata = DataFrame({"valor": smc},index=input[0].index)
        data_ = data[["valor"]].rename(columns={"valor":"output"}).join(input[0][["valor"]].rename(columns={"valor":"pma"})).join(input[1][["valor"]].rename(columns={"valor":"etp"})).join(input[2][["valor"]].rename(columns={"valor":"q_obs"})).join(input[3][["valor"]].rename(columns={"valor":"smc_obs"}))
        return (
            [data, smcdata], 
            ProcedureFunctionResults({
                "data": data_
            })
        )