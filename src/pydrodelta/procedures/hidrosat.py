import logging
import numpy as np
from pandas import DataFrame, Series, concat
from typing import Union, List, Tuple
from ..procedure_function import ProcedureFunctionResults
from ..procedures.pq import PQProcedureFunction
from ..pydrology import HIDROSAT, HIDROSATPowerLawReservoir, RetentionReservoir, LinearReservoirCascade
from ..validation import getSchemaAndValidate
from ..model_state import ModelState

class HIDROSATProcedureFunction(PQProcedureFunction):
    """Modelo PQ HIDROSAT para macrosistemas de llanura húmeda"""

    @property
    def S0(self) -> float:
        """Almacenamiento máximo en reservorio de retención (Agua de Tensión en perfil de suelo) / Maximum Retention Capacity [mm]"""
        return self.parameters["S0"]
    
    @property
    def K(self) -> float:
        """Tiempo de residencia (propagación escorrentía de interfluvios a flujo encauzado en valle) / Residence Time delayed runoff - Discrete Linear Reservoir Cascade Approach - [days]"""
        return self.parameters["K"]
    
    @property
    def N(self) -> float:
        """Número de reservorios en serie (propagación escorrentía de interfluvios a flujo encauzado en valle) / Number of Reservoirs - Discrete Linear Reservoir Cascade Approach - [1]"""
        return self.parameters["N"]
    
    @property
    def W0(self) -> float:
        """Almacenamiento Máximo en reservorio de Detención (valle) / Maximum Detention Capacity [mm]"""
        return self.parameters["W0"]
    
    @property
    def Q0(self) -> float:
        """Caudal Máximo (flujo encauzado en valle) / Maximum Discharge [mm]"""
        return self.parameters["Q0"]
    
    @property
    def gamma(self) -> float:
        """Factor de forma. Ley de Potencia reservorio de Detención / shape factor power law reservoir [-]"""
        return self.parameters["gamma"]
    
    @property
    def maxFlooded(self) -> float:
        """Área anegada máxima (fracción del sistema) / maximum flooded area [-]"""
        return self.parameters["maxFlooded"] if "MaxFlooded" in self.parameters else 1
    
    @property
    def detentionRatio(self) -> float:
        """Coeficiente de prorateo entre aporte directo y aporte demorado en red de drenaje  / diversion ratio direct rainfall (detention/drainfall) [-]"""
        return self.parameters["detentionRatio"] if "detentionRatio" in self.parameters else 1
    
    @property
    def epsilon(self) -> float:
        """Valor umbral de tolerancia error en Newton-Raphson / Tolerance threshold Newton-Raphson [mm]"""
        return self.parameters["epsilon"] if "epsilon" in self.parameters else 0.0001
    
    @property
    def dt(self) -> float:
        """Longitud de subpaso de cómputo en Newton-Raphson / time step resolution Newton-Raphson [-]"""
        return self.extra_pars["dt"] if "dt" in self.extra_pars else 1
    
    @property
    def soilStorage(self) -> float:
        """Almacenamiento inicial en reservorio de retención / Initial tension water storage [mm]"""
        return self.initial_states[0] if isinstance(self.initial_states,(list,tuple)) and len(self.initial_states) > 1 else self.initial_states["soilStorage"] if isinstance(self.initial_states,dict) and "soilStorage" in self.initial_states  else [0]
    
    @property
    def Runoff(self) -> float:
        """Escorrentía inicial / Initial Runoff [mm]"""
        return self.initial_states[1] if isinstance(self.initial_states,(list,tuple)) and len(self.initial_states) > 1 else self.initial_states["Runoff"] if isinstance(self.initial_states,dict) and "Runoff" in self.initial_states  else [0]
    
    @property
    def floodPlainStorage(self) -> float:
        """Almacenamiento inicial en reservorio de detención / Initial floodplain Storage [mm]"""
        return self.initial_states[1] if isinstance(self.initial_states,(list,tuple)) and len(self.initial_states) > 1 else self.initial_states["floodPlainStorage"] if isinstance(self.initial_states,dict) and "floodPlainStorage" in self.initial_states  else [0]
    
    @property
    def Flooded(self) -> float:
        """Extensión inicial de anegamiento  / Initial flooded area [mm]"""
        return self.initial_states[1] if isinstance(self.initial_states,(list,tuple)) and len(self.initial_states) > 1 else self.initial_states["Flooded"] if isinstance(self.initial_states,dict) and "Flooded" in self.initial_states  else [0]
    
    @property
    def engine(self) -> HIDROSAT:
        """Reference to the hydrologic procedure engine (see ..pydrology.HIDROSAT)"""
        return self._engine
    
    def setEngine(
            self,
            input : List[List[float]]
        ) -> None:
        """Set HIDROSAT procedure engine
        Args:
            input : list - boundary conditions: list of (pmad, etpd)
        """
        hidrosat_pars=[self.S0,self.K,self.N,self.W0,self.Q0,self.gamma,self.maxFlooded,self.detentionRatio,self.epsilon]
        self._engine=HIDROSAT(
            pars=hidrosat_pars,
            Boundaries=input,
            InitialConditions=[self.soilStorage,self.Runoff,self.floodPlainStorage,self.Flooded])
    
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
            - S0 
            - K
            - N
            - W0
            - Q0 
            - gamma
            - maxFloodedArea (optional, by default 1)
            - detentionRatio (optional, by default 1)
            - epsilon (optional, by default 0.001)
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
            "HIDROSATProcedureFunction")
        
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
        pma = list(input[0].valor) 
        etp = list(input[1].valor)
        if len(etp) < len(pma):
            raise Exception("etp boundary length must be the same as pma")
        if len(input) > 2:
            inflow=list(input[2].valor)
            if len(inflow) < len(pma):
                raise Exception("inflow boundary length must be the same as pma")
            else:
                self.Boundaries = [ (x, etp[i],inflow[i]) for i, x in enumerate(pma)]        
                self.setEngine(
                    input = [ list(input[0].valor), list(input[1].valor), list(input[2].valor) ] 
                )
        else:
            self.Boundaries = [ (x, etp[i]) for i, x in enumerate(pma)]
            self.setEngine(
                input = [ list(input[0].valor), list(input[1].valor) ] 
            )
        self.engine.executeRun()
        q_sim = [x / 1000 / 24 / 60 / 60 * self.area * self.ae for x in self.engine.Q]
        q_sim = q_sim[0:len(self.Boundaries)] 
        q_sim = DataFrame({"valor": q_sim},index=input[0].index)
        smc_sim = [(self.rho - self.wp) * x / self.S0 + self.wp for x in self.engine.soilStorage[0:len(self.Boundaries)]]
        smc_sim = DataFrame({"valor": smc_sim},index=input[0].index)
        data_ = q_sim[["valor"]].rename(columns={"valor":"output"}).join(input[0][["valor"]].rename(columns={"valor":"pma"})).join(input[1][["valor"]].rename(columns={"valor":"etp"})).join(input[2][["valor"]].rename(columns={"valor":"q_obs"}))
        data_["evapoTranspiration"] = self.engine.EVSoil[0:len(self.Boundaries)]
        data_["soilStorage"] = self.engine.soilStorage[0:len(self.Boundaries)]
        data_["freeWater"] = self.engine.freeWater[0:len(self.Boundaries)]
        data_["delayedRunoff"] = self.engine.Runoff[0:len(self.Boundaries)]
        data_["directRunoff"] = self.engine.DirectRunoff[0:len(self.Boundaries)]
        data_["evaporationFloodPlain"] = self.engine.EVFloodPlain[0:len(self.Boundaries)]
        data_["floodplainStorage"] = self.engine.floodplainStorage[0:len(self.Boundaries)]
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

#Todo: Declarar procesos en HIDROSAT(pydrology) como están declarados en HOSH para que los reconozca en lin. 80. 
    