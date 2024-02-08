import logging
# from numpy import tanh
# from typing import Optional
# from pydrodelta.series_data import SeriesData
import numpy as np
from pandas import DataFrame, Series, concat
from typing import Union

from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.procedures.pq import PQProcedureFunction
from pydrodelta.pydrology import HOSH4P1L, triangularDistribution
from pydrodelta.validation import getSchemaAndValidate
from pydrodelta.model_state import ModelState

class HOSH4P1LProcedureFunction(PQProcedureFunction):
    """Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base)."""

    _states = [
        ModelState(name="SurfaceStorage",constraints=(0,np.inf),default=0),
        ModelState(name="SoilStorage",constraints=(0,np.inf),default=0)
    ]
    """Model states: SurfaceStorage, SoilStorage"""

    def __init__(
        self,
        **kwargs):
        super().__init__(**kwargs)
        getSchemaAndValidate(kwargs,"HOSH4P1LProcedureFunction")
        self.maxSurfaceStorage = self.parameters["maxSurfaceStorage"]
        self.maxSoilStorage = self.parameters["maxSoilStorage"]
        self.Proc = self.parameters["Proc"] if "Proc" in self.parameters else "UH"
        self.T = self.parameters["T"] if "T" in self.parameters else None
        self.distribution = self.parameters["distribution"] if "distribution" in self.parameters else "Symmetric"
        self.dt = self.extra_pars["dt"] if "dt" in self.extra_pars else 0.01
        self.shift = self.extra_pars["shift"] if "shift" in self.extra_pars else False
        self.approx = self.extra_pars["approx"] if "aprrox" in self.extra_pars else False
        self.k = self.parameters["k"] if "k" in self.parameters else None
        self.n = self.parameters["n"] if "n" in self.parameters else None
        self.SurfaceStorage = self.initial_states[0] if len(self.initial_states) > 0 else [0]
        self.SoilStorage = self.initial_states[1] if len(self.initial_states) > 1 else [0]
        if self.Proc == "UH" and self.T is None:
            raise Exception("Missing parameter T")
        if self.Proc == "Nash" and self.k is None:
            raise Exception("Missing parameter k")
        if self.Proc == "Nash" and self.n is None:
            raise Exception("Missing parameter n")
    def run(
        self,
        input : list = None
        ) -> tuple:
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        if self.Proc == 'UH':
            dist = triangularDistribution(self.T,distribution=self.distribution,dt=self.dt,shift="T" if self.shift else "F",approx="T" if self.approx else "F")
            hosh_pars = [self.maxSurfaceStorage,self.maxSoilStorage,dist]
        else:
            hosh_pars = [self.maxSurfaceStorage,self.maxSoilStorage,self.n,self.k]
        pma = input[0]["valor"].to_list()
        etp = input[1]["valor"].to_list()
        if len(etp) < len(pma):
            raise Exception("etp boundary length must be the same as pma")
        self.Boundaries = [ (x, etp[i]) for i, x in enumerate(pma)]
        self.engine = HOSH4P1L(pars=hosh_pars,Boundaries=np.array(self.Boundaries),InitialConditions=[self.SurfaceStorage,self.SoilStorage],Proc=self.Proc)
        self.engine.executeRun()
        q_sim = [x / 1000 / 24 / 60 / 60 * self.area * self.ae for x in self.engine.Q]
        q_sim = q_sim[0:len(self.Boundaries)]
        q_sim = DataFrame({"valor": q_sim},index=input[0].index)
        smc_sim = [(self.rho - self.wp) * x / self.maxSoilStorage + self.wp for x in self.engine.SoilStorage[0:len(self.Boundaries)]]
        smc_sim = DataFrame({"valor": smc_sim},index=input[0].index)
        data_ = q_sim[["valor"]].rename(columns={"valor":"output"}).join(input[0][["valor"]].rename(columns={"valor":"pma"})).join(input[1][["valor"]].rename(columns={"valor":"etp"})).join(input[2][["valor"]].rename(columns={"valor":"q_obs"}))
        data_["SurfaceStorage"] = self.engine.SurfaceStorage[0:len(self.Boundaries)]
        data_["SoilStorage"] = self.engine.SoilStorage[0:len(self.Boundaries)]
        data_["NetRainfall"] = self.engine.NetRainfall[0:len(self.Boundaries)]
        data_["Infiltration"] = self.engine.Infiltration[0:len(self.Boundaries)]
        data_["Runoff"] = self.engine.Runoff[0:len(self.Boundaries)]
        data_["EVR1"] = self.engine.EVR1[0:len(self.Boundaries)]
        data_["EVR2"] = self.engine.EVR2[0:len(self.Boundaries)]
        return (
            [q_sim,smc_sim], 
            ProcedureFunctionResults({
                "data": data_
            })
        )

    def setInitialStates(
        self, 
        states: Union[list,tuple] = []
        ) -> None:
        super().setInitialStates(states)
        self.SurfaceStorage = self.initial_states["SurfaceStorage"]
        self.SoilStorage = self.initial_states["SoilStorage"]
