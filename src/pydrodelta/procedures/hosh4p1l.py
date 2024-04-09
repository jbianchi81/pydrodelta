import logging
# from numpy import tanh
# from typing import Optional
# from pydrodelta.series_data import SeriesData
import numpy as np
from pandas import DataFrame, Series, concat
from typing import Union, List, Tuple

from ..procedure_function import ProcedureFunctionResults
from ..procedures.pq import PQProcedureFunction
from ..pydrology import HOSH4P1L, triangularDistribution
from ..validation import getSchemaAndValidate
from ..model_state import ModelState

class HOSH4P1LProcedureFunction(PQProcedureFunction):
    """Modelo Operacional de Transformación de Precipitación en Escorrentía de 4 parámetros (estimables). Hidrología Operativa Síntesis de Hidrograma. Método NRCS, perfil de suelo con 2 reservorios de retención (sin efecto de base)."""

    _states = [
        ModelState(name="SurfaceStorage",constraints=(0,np.inf),default=0),
        ModelState(name="SoilStorage",constraints=(0,np.inf),default=0)
    ]
    """Model states: SurfaceStorage, SoilStorage"""

    @property
    def maxSurfaceStorage(self) -> float:
        "Maximum surface storage (model parameter)"
        return self.parameters["maxSurfaceStorage"]
    
    @property
    def maxSoilStorage(self) -> float:
        """Maximum soil storage (model parameter)"""
        return self.parameters["maxSoilStorage"]
    
    @property
    def Proc(self) -> str:
        """Routing procedure (model parameter)"""
        return self.parameters["Proc"] if "Proc" in self.parameters else "UH"
    
    @property
    def T(self) -> float:
        """Triangular hydrogram time to peak (model parameter)"""
        return self.parameters["T"] if "T" in self.parameters else None
    
    @property
    def distribution(self) -> str:
        """Triangular hydrogram distribution (model parameter)"""
        return self.parameters["distribution"] if "distribution" in self.parameters else "Symmetric"

    @property
    def dt(self) -> float:
        """Computation step (procedure configuration)"""
        return self.extra_pars["dt"] if "dt" in self.extra_pars else 0.01

    @property
    def shift(self) -> bool:
        """shift (procedure configuration)"""
        return bool(self.extra_pars["shift"]) if "shift" in self.extra_pars else False

    @property
    def approx(self) -> bool:
        """approx (procedure configuration)"""
        return bool(self.extra_pars["approx"]) if "approx" in self.extra_pars else False
           
    @property
    def k(self) -> float:
        """Nash linear channel coefficient k (model parameter)"""
        return self.parameters["k"] if "k" in self.parameters else None

    @property
    def n(self) -> float:
        """Nash linear channel number of reservoirs n (model parameter)"""
        return self.parameters["n"] if "n" in self.parameters else None
        
    @property
    def SurfaceStorage(self) -> float:
        """Initial surface storage [mm] (model initial state)"""
        return self.initial_states[0] if isinstance(self.initial_states,(list,tuple)) and len(self.initial_states) > 0 else self.initial_states["SurfaceStorage"] if isinstance(self.initial_states,dict) and "SurfaceStorage" in self.initial_states  else [0]

    @property
    def SoilStorage(self) -> float:
        """Initial soil storage [mm] (model initial state)"""
        return self.initial_states[1] if isinstance(self.initial_states,(list,tuple)) and len(self.initial_states) > 1 else self.initial_states["SoilStorage"] if isinstance(self.initial_states,dict) and "SoilStorage" in self.initial_states  else [0]
    
    @property
    def engine(self) -> HOSH4P1L:
        """Reference to the hydrologic procedure engine (see ..pydrology.HOSH4P1L)"""
        return self._engine
    
    def setEngine(
            self,
            input : list
        ) -> None:
        """Set HOSH4P1L procedure engine
        
        Args:
            input : list - boundary conditions: list of (pmad, etpd)
        """
        if self.Proc == 'UH':
            dist = triangularDistribution(
                self.T,
                distribution = self.distribution,
                dt = self.dt,
                shift = "T" if self.shift else "F",
                approx="T" if self.approx else "F")
            hosh_pars = [self.maxSurfaceStorage,self.maxSoilStorage,dist]
        else:
            hosh_pars = [self.maxSurfaceStorage,self.maxSoilStorage,self.n,self.k]
        self._engine = HOSH4P1L(
            pars = hosh_pars,
            Boundaries = np.array(input),
            InitialConditions = [self.SurfaceStorage,self.SoilStorage],
            Proc = self.Proc)

    _required_extra_pars : list = ["area", "ae", "rho", "wp"]
    """When inheriting this class, override this property according to the procedure requirements. Method self.setBasinMetadata iterates this list to check for missing extra parameters (e.g. basin parameters)"""

    def __init__(
        self,
        parameters : Union[list,tuple,dict],
        extra_pars : Union[list,tuple,dict],
        initial_states : Union[list,tuple,dict],
        **kwargs):
        """
        parameters  : Union[list,tuple,dict]
            
            Ordered list or dict
            
            Properties:
            - maxSurfaceStorage
            - maxSoilStorage
            - Proc (optional, default "UH")
            - T (optional, default None)
            - distribution (optional, default "Symmetric")
            - k (optional, default None)
            - n (optional, default None)
        """
        super().__init__(
            parameters = parameters,
            extra_pars = extra_pars,
            initial_states = initial_states,
            **kwargs)
        getSchemaAndValidate(
            dict(
                kwargs,
                parameters = parameters,
                extra_pars = extra_pars,
                initial_states = initial_states
            ),
            "HOSH4P1LProcedureFunction")
        if self.Proc == "UH" and self.T is None:
            raise Exception("Missing parameter T")
        if self.Proc == "Nash" and self.k is None:
            raise Exception("Missing parameter k")
        if self.Proc == "Nash" and self.n is None:
            raise Exception("Missing parameter n")
    def run(
        self,
        input : List[DataFrame] = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Parameters:
        -----------
        input : list of DataFrames
            Boundary conditions. If None, runs .loadInput

        Returns:
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        pma = input[0]["valor"].to_list()
        etp = input[1]["valor"].to_list()
        if len(etp) < len(pma):
            raise Exception("etp boundary length must be the same as pma")
        self.Boundaries = [ (x, etp[i]) for i, x in enumerate(pma)]
        self.setEngine(
            input = [ (x, etp[i]) for i, x in enumerate(pma) ]
        )
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
            ProcedureFunctionResults(
                data = data_
            )
        )

    def setInitialStates(
        self, 
        states: Union[list,tuple] = []
        ) -> None:
        """Initial states setter
        
        Parameters:
        -----------
        states: Union[list,tuple]
        
            (SurfaceStorage : float, SoilStorage : float)"""
        super().setInitialStates(states)
