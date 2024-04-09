import numpy as np
from pandas import DataFrame
from typing import Union, List, Tuple
import logging

from ..procedure_function import ProcedureFunctionResults
from ..procedures.pq import PQProcedureFunction
from ..pydrology import GR4J
from ..model_parameter import ModelParameter
from ..model_state import ModelState
from numpy import inf

class GR4JProcedureFunction(PQProcedureFunction):
    """Modelo Operacional de Transformación de Precipitación en Escorrentía de Ingeniería Rural de 4 parámetros (CEMAGREF). A diferencia de la versión original, la convolución se realiza mediante producto de matrices. Parámetros: Máximo almacenamiento en reservorio de producción, tiempo al pico (hidrograma unitario),máximo almacenamiento en reservorio de propagación, coeficiente de intercambio."""

    @property
    def X0(self) -> float:
        """capacite du reservoir de production (mm)"""
        return self.parameters["X0"]
    @property
    def X1(self) -> float:
        """capacite du reservoir de routage (mm)"""
        return self.parameters["X1"]
    @property
    def X2(self) -> float:
        """facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)"""
        return self.parameters["X2"]
    @property
    def X3(self) -> float:
        """temps de base de l'hydrogramme unitaire (d)"""
        return self.parameters["X3"]
    @property
    def Sk_init(self) -> float:
        """Initial soil storage"""
        return self.initial_states["Sk"] if "Sk" in self.initial_states else 0
    @property
    def Rk_init(self) -> float:
        """Initial routing storage"""
        return self.initial_states["Rk"] if "Rk" in self.initial_states else 0
    @property
    def dt(self) -> float:
        """Time step duration [days]"""
        return self.extra_pars["dt"] if "dt" in self.extra_pars else 1

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
    """Procedure function parameter definitions"""

    _states = [
        #  id | model_id | nombre | range_min | range_max | def_val | orden 
        # ----+----------+--------+-----------+-----------+---------+-------
        ModelState(name='Sk', constraints=(0,inf), default=0),
        #  23 |       38 | Sk     |         0 |  Infinity |       0 |     1
        ModelState(name='Rk', constraints=(0,inf), default=0)
        #  24 |       38 | Rk     |         0 |  Infinity |       0 |     2

    ]
    """Procedure function states definitions"""

    @property
    def engine(self) -> GR4J:
        """Reference to instance of GR4J procedure engine"""
        return self._engine

    _required_extra_pars : list = ["area", "ae", "rho", "wp"]
    """When inheriting this class, override this property according to the procedure requirements. Method self.setBasinMetadata iterates this list to check for missing extra parameters (e.g. basin parameters)"""


    def __init__(
        self,
        parameters : Union[list,tuple,dict],
        initial_states : Union[list,tuple,dict] = None,
        extra_pars : dict = None,
        **kwargs
        ):
        """
        parameters : list or tuple or dict

            If list or tuple: (X0 : float, X1 : float, X2 : float, X3 : float)

            If dict: {"X0": float, "X1": float, "X2": float, "X3": float}

            Where:
            - X0:	capacite du reservoir de production (mm)
            - X1:	capacite du reservoir de routage (mm)
            - X2:	facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)
            - X3:	temps de base de l'hydrogramme unitaire (d)
        
        initial_states: list, tuple or dict

            If list or tuple: (Sk_init : float, Rk_init : float)

            If dict: {"Sk_init": float, "Rk_init": float}

            where:
            - Sk_init: Initial soil storage [mm]
            - Rk_init: Initial routing storage [mm]

        extra_pars : dict = None

            Additional, non-calibratable parameters

            Properties:
            - dt : float

                Time step duration (days, default 1)
|
        \**kwargs : keyword arguments (see ProcedureFunction)"""
        super().__init__(
            parameters=parameters, 
            initial_states=initial_states,
            extra_pars=extra_pars,
            **kwargs)
        self._engine = None
    
    def run(
        self,
        input : List[DataFrame] = None
        ) -> Tuple[list, dict]:
        """
        Runs the procedure function.
        
        Parameters:
        -----------
        
        input : List[DataFrame] = None
        
            If input is None, it loads the boundaries. Else, input must be a list of DataFrames
        
        Returns:
        --------
        
        Tuple[List[DataFrame], ProcedureFunctionResults]
            
            Devuelve una lista de DataFrames (uno por output del procedimiento) y opcionalmente un objeto ProcedureFunctionResults
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        self.setEngine([ ( input[0]["valor"][i], input[1]["valor"][i]) for i in range(len(input[0])) ])
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
            ProcedureFunctionResults(
                data = data_,
                states = data_[["SoilStorage","RoutingStorage","Runoff","Inflow","Leakages"]]
            )
        )
    
    def setEngine(
        self,
        input : List[Tuple[float,float]]
        ) -> None:
        """Instantiate GR4J procedure engine using input as Boundaries
        
        Args:
        input : List[Tuple[float,float]] - Boundary conditions: list of (pmad : float, etpd : float)"""
        self._engine = GR4J(
            pars=[self.X0,self.X3,self.X2,self.X1],
            Boundaries=np.array(input),
            InitialConditions=[self.Sk_init,self.Rk_init])
    
    def setParameters(
        self,
        parameters : Union[list, tuple] = []
        ) -> None:
        """Set parameters from ordered list
        
        Parameters:
        -----------
        parameters : Union[list, tuple] = []

            (X0 : float, X1 : float, X2 : float, X3 : float)
            
            Where:
            - X0:	capacite du reservoir de production (mm)
            - X1:	capacite du reservoir de routage (mm)
            - X2:	facteur de l'ajustement multiplicatif de la pluie efficace (sans dimension)
            - X3:	temps de base de l'hydrogramme unitaire (d)

        """
        super().setParameters(parameters)

    def setInitialStates(
        self,
        states : Union[list, tuple] = []
        ):
        """Set initial states from ordered list
        
        Parameters:
        -----------
        states : Union[list, tuple] = []
        
            (Sk_init : float, Rk_init : float)

            where:
            - Sk_init: Initial soil storage [mm]
            - Rk_init: Initial routing storage [mm]
        """
        super().setInitialStates(states)
