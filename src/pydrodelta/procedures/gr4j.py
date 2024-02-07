import logging
# from numpy import tanh
# from typing import Optional
# from pydrodelta.series_data import SeriesData
import numpy as np
from pandas import DataFrame, Series, concat
from typing import Union

from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.procedures.pq import PQProcedureFunction
from pydrodelta.pydrology import GR4J
from pydrodelta.model_parameter import ModelParameter
from pydrodelta.model_state import ModelState
from numpy import inf

class GR4JProcedureFunction(PQProcedureFunction):

    _parameters = [
        #  id  | model_id | nombre | lim_inf | range_min | range_max | lim_sup  | orden 
        # -----+----------+--------+---------+-----------+-----------+----------+-------
        ModelParameter(name="X0",constraints=(1e-09, 100, 3000, inf)),
        #  169 |       32 | a      |   1e-09 |       100 |      1200 | Infinity |     1
        ModelParameter(name="X1",constraints=(-200, -5, 3, inf)),
        #  170 |       32 | b      |    -200 |        -5 |         3 | Infinity |     2
        ModelParameter(name="X2",constraints=(1e-09, 20, 300, inf)),
        #  171 |       32 | c      |   1e-09 |        20 |       300 | Infinity |     3
        ModelParameter(name="X3",constraints=(1e-09, 1.1, 2.9, inf))
        #  172 |       32 | d      |   1e-09 |       1.1 |       2.9 | Infinity |     4
    ]

    _states = [
        #  id | model_id | nombre | range_min | range_max | def_val | orden 
        # ----+----------+--------+-----------+-----------+---------+-------
        ModelState(name='Sk', constraints=(0,inf), default=0),
        #  23 |       38 | Sk     |         0 |  Infinity |       0 |     1
        ModelState(name='Rk', constraints=(0,inf), default=0)
        #  24 |       38 | Rk     |         0 |  Infinity |       0 |     2

    ]

    def __init__(self,params,procedure):
        super().__init__(params,procedure) # super(PQProcedureFunction,self).__init__(params,procedure)
        self.X0 = self.parameters["X0"]
        """X0	capacite du reservoir de production (mm)"""
        self.X1 = self.parameters["X1"]
        """X1	capacite du reservoir de routage (mm)"""
        self.X2 = self.parameters["X2"]
        """X2	facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)"""
        self.X3 = self.parameters["X3"]
        """X3	temps de base de l'hydrogramme unitaire (d)"""

        self.Sk_init = self.initial_states["Sk"] if "Sk" in self.initial_states else 0
        """Initial Soil Storage"""
        self.Rk_init = self.initial_states["Rk"] if "Rk" in self.initial_states else 0
        """Initial Routing Storage"""

        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 1
        """Time step duration (days, default 1)"""        

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
        data_ = data[["valor"]].rename(
                columns={"valor":"output"}
            ).join(
                input[0][["valor"]].rename(columns={"valor":"pma"})
            ).join(
                input[1][["valor"]].rename(columns={"valor":"etp"})
            ).join(
                input[2][["valor"]].rename(columns={"valor":"q_obs"})
            ).join(
                input[3][["valor"]].rename(columns={"valor":"smc_obs"})
            ).join(
                DataFrame({"SoilStorage": self.engine.prodStore.SoilStorage[0:len(input[0].index)]}, index=input[0].index)
            ).join(
                DataFrame({"Runoff": self.engine.Runoff[0:len(input[0].index)]}, index=input[0].index)
            ).join(
                DataFrame({"Inflow": self.engine.routStore.Inflow[0:len(input[0].index)]}, index=input[0].index)
            ).join(
                DataFrame({"Leakages": self.engine.routStore.Leakages[0:len(input[0].index)]}, index=input[0].index)
            ).join(
                DataFrame({"RoutingStorage": self.engine.routStore.Storage[0:len(input[0].index)]}, index=input[0].index)
            )
        return (
            [data, smcdata], 
            ProcedureFunctionResults({
                "data": data_,
                "states": data_[["SoilStorage","RoutingStorage","Runoff","Inflow","Leakages"]]
            })
        )
    
    def setParameters(self,parameters:Union[list,tuple]=[]):
        super().setParameters(parameters)
        self.X0 = self.parameters["X0"]
        self.X1 = self.parameters["X1"]
        self.X2 = self.parameters["X2"]
        self.X3 = self.parameters["X3"]

    def setInitialStates(self,states:Union[list,tuple]=[]):
        super().setInitialStates(states)
        self.Sk_init = self.initial_states["Sk"]
        self.Rk_init = self.initial_states["Rk"]
