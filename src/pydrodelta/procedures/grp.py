import logging
from numpy import tanh
# from typing import Optional
# from pydrodelta.series_data import SeriesData
from pandas import DataFrame, Series, concat
from typing import Union, List, Tuple
from numpy import inf, isnan

from ..procedure_function import ProcedureFunctionResults
from ..model_parameter import ModelParameter
from ..model_state import ModelState
from .pq import PQProcedureFunction
from ..descriptors.bool_descriptor import BoolDescriptor
from ..descriptors.list_descriptor import ListDescriptor

class GRPProcedureFunction(PQProcedureFunction):
    """L'équipe du Cemagref a développé un logiciel de prévision hydrologique (GRP) pour le Service central d'hydrométéorologie et d'appui à la prévision des inondations (SCHAPI), conçu pour prédire les crues des cours d'eau. Les chercheurs expliquent que les observations et prévisions des précipitations du réseau Météo-France pour les bassins correspondants sont exploitées par le logiciel. L'indice d'humidité des sols est également un facteur pris en compte par le logiciel."""
    _parameters = [
        ModelParameter(name="X0",constraints=(0.0001,10,1200,inf)),
        ModelParameter(name="X1",constraints=(0.0001,10,1200,inf)),
        ModelParameter(name="X2",constraints=(0.0001,0.1,1,inf)),
        ModelParameter(name="X3",constraints=(0.0001,1.1,10,inf))
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
    """Procedure function state definitions"""

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
    def windowsize(self) -> int:
        """time window size"""
        return self.extra_pars["windowsize"] if "windowsize" in self.extra_pars else None
    
    @property
    def rho(self) -> float:
        """rho soil porosity [0-1]"""
        return self.extra_pars["rho"] if "rho" in self.extra_pars else 0.5
    
    @property
    def wp(self) -> float:
        """wp soil wilting point [0-1]"""
        return self.extra_pars["wp"] if "wp" in self.extra_pars else 0.03
    
    @property
    def ae(self) -> float:
        """ae effective area [0-1]"""
        return self.extra_pars["ae"] if "ae" in self.extra_pars else 1
    
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
        """computation step of the unit hydrograph"""
        return 1

    @property
    def alpha(self) -> float:
        """exponent of the unit hydrograph"""
        return 5/2

    UH1 = ListDescriptor()
    """Pulses unit hydrograph"""
    
    SH1 = ListDescriptor()
    """Accumulated unit hidrigraph"""

    update = BoolDescriptor()
    """Update states with observed discharge"""

    def __init__(
        self,
        parameters : Union[list,tuple,dict],
        initial_states : Union[list,tuple,dict] = None,
        update = False,
        **kwargs):
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

        update : bool = False

            Update model states when discharge observations are available
|
        \**kwargs : keyword arguments (see ProcedureFunction)
        """
        super().__init__(
            parameters = parameters,
            initial_states = initial_states,
            **kwargs)
        
        self.UH1, self.SH1 = GRPProcedureFunction.createUnitHydrograph(self.X3, self.alpha)
        self.update = update

    @staticmethod
    def createUnitHydrograph(
        X3 : float,
        alpha : float
        ) -> Tuple[list,list]:
        """Creates unit hydrograph
        
        Parameters:
        -----------
        X3 : float
            Unit hydrograph base time
        
        alpha : float
            Unit hydrograph exponent
        
        Returns:
        --------
        Tuple[list,list] : where first element is the pulses Unit hydrograph and the second is the accumulated unit hydrograph"""
        t = 0
        UH1 = []
        SH1 = []
        while t <= int(X3):
            # logging.info("t: %i" % t)
            if t == 0:
                UH1.append(0)
                SH1.append(0)
            else:
                if t <= X3:
                    SH1.append(t**alpha/(t**alpha+(X3-t)**alpha))
                else:
                    SH1.append(1)
                UH1.append(SH1[t]-SH1[t-1])
            t = t + 1
        return UH1, SH1

    def run(
        self,
        input : List[DataFrame] = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults

        Parameters:
        -----------
        input : list of DataFrames
            Boundary conditions. If None, runs .loadInput

        Returns:
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
        -------- 
        """
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        results = DataFrame({
            "timestart": Series(dtype='datetime64[ns]'),
            "pma": Series(dtype='float'),
            "etp": Series(dtype='float'),
            "q_obs": Series(dtype='float'),
            "smc_obs": Series(dtype='float'),
            "Sk": Series(dtype='float'),
            "Rk": Series(dtype='float'),
            "q": Series(dtype='float'),
            "smc": Series(dtype='float'),
            "k": Series(dtype='int'),
            "runoff": Series(dtype="float"), 
            "inflow": Series(dtype="float"),
            "leakages": Series(dtype="float")
        })
        results.set_index("timestart", inplace=True)
        # initialize states
        Sk = min(self.Sk_init,self.X0)
        self.Pr = []
        k = -1
        Rk = self.Rk_init # *self.X2

        # series: pma*, etp*, q_obs, smc_obs [*: required]
        if len(input) < 2:
            raise Exception("Missing input series: at least pma and etp required")
        # instantiate lists for statistics computation
        sim = []
        obs = []
        # iterate series using pma's index:
        for i, row in input[0].iterrows():
            k = k + 1
            pma = row["valor"]
            etp = input[1].loc[[i]].valor.item()
            q_obs = input[2].loc[[i]].valor.item() if len(input) > 2 else None
            smc_obs = input[3].loc[[i]].valor.item() if len(input) > 3 else None
            smc = (self.rho-self.wp)*Sk/self.X0+self.wp
            if isnan(pma):
                if self.fill_nulls:
                    logging.warn("Missing pma value for date: %s. Filling up with 0" % i)
                    pma = 0
                else:
                    logging.warn("Missing pma value for date: %s. Unable to continue" % i)
                    break
            if isnan(etp):
                if self.fill_nulls:
                    logging.warn("Missing etp value for date: %s. Filling up with 0" % i)
                    etp = 0
                else:
                    logging.warn("Missing etp value for date: %s. Unable to continue" % i)
                    break
            Sk_, Rk_, q, runoff, inflow, leakages = self.advance_step(Sk, Rk, pma, etp, k, q_obs)
            new_row = DataFrame([[i, pma, etp, q_obs, smc_obs, Sk, Rk, q, smc, k, runoff, inflow, leakages]], columns= ["timestart", "pma", "etp", "q_obs", "smc_obs", "Sk", "Rk", "q", "smc", "k", "runoff", "inflow", "leakages"])
            results = concat([results,new_row])
            Sk = Sk_
            Rk = Rk_
            if q_obs is not None:
                sim.append(q)
                obs.append(q_obs)
        results = results.set_index("timestart")
        # logging.debug(str(results))
        procedure_results = ProcedureFunctionResults(
            border_conditions = results[["pma","etp","q_obs","smc_obs"]],
            initial_states = {
                "Sk": self.Sk_init,
                "Rk": self.Rk_init
            },
            states = results[["Sk","Rk","runoff","inflow","leakages"]].rename(columns={"Sk":"SoilStorage","Rk":"RoutingStorage","runoff":"Runoff","inflow":"Inflow","leakages":"Leakages"}),
            parameters = {
                "X0": self.X0,
                "X1": self.X1,
                "X2": self.X2,
                "X3": self.X3,
                "area": self.area,
                "windowsize": self.windowsize,
                "rho": self.rho,
                "wp": self.wp,
                "ae": self.ae
            },
            data = results
        )
        return (
            [results[["q"]].rename(columns={"q":"valor"}),results[["smc"]].rename(columns={"smc":"valor"})],
            procedure_results
        )
    
    def advance_step(
        self,
        Sk: float,
        Rk: float,
        pma: float,
        etp: float,
        k: int,
        q_obs=None
        ) -> Tuple[float,float,float,float,float,float]:
        """Advances model time step
        
        Parameters:
        -----------
        Sk : float

            Soil Storage
            
        Rk : float

            Routing storage
        
        pma : float

            Mean areal precipitation
        
        etp : float

            Potential evapotranspiration
        
        k : int 

            Time step index
        
        q_obs : float or None

            observed discharge
        
        Returns:
        --------
        Tuple[float,float,float,float,float,float] : (Sk_, Rk_, Qk, Qr, self.X2*(Perc+Pn-Ps), R1 - R1**2/(R1+self.X1)"""
        Pn = pma - etp if pma >= etp else 0
        Ps = self.X0*(1-(Sk/self.X0)**2)*tanh(Pn/self.X0)/(1+Sk/self.X0*tanh(Pn/self.X0)) if Pn > 0 else 0
        Es = Sk*(2-Sk/self.X0)*tanh((etp-pma)/self.X0)/(1+(1-Sk/self.X0)*tanh((etp-pma)/self.X0)) if Pn == 0 else 0
        S1 = Sk + Ps - Es
        Perc = S1*(1-(1+(4/9*S1/self.X0)**4)**(-1/4))
        Sk_ = S1 - Perc
        self.Pr.append(self.X2*(Perc+Pn-Ps))
        Quh = self.computeUnitHydrograph(k)
        R1 = max(0, Rk+Quh)
        # update with q_obs (disabled by default)
        if q_obs is not None and self.update:
            Qt = q_obs*1000*24*60*60*self.dt/self.area/self.ae
            R1 = ((Qt**2+4*self.X1*Qt)**0.5+Qt)/2
        Qr = R1**2/(R1+self.X1)
        Qk = Qr/1000/24/60/60/self.dt*self.area*self.ae
        Rk_ = R1 - Qr
        return Sk_, Rk_, Qk, Qr, self.X2*(Perc+Pn-Ps), R1 - R1**2/(R1+self.X1)

    def computeUnitHydrograph(
        self,
        k : int) -> list:
        """Compute unit hydrograph discharge for time step k
        
        Parameters:
        -----------
        k : int

            Time step index
        
        Returns:
        --------
        discharge : float"""

        j = 0
        Quh = 0
        while(j<min(int(self.X3)+1,k)):
            # logging.debug("j: %i, UH1[j]: %f" % (j,self.UH1[j]))
            # logging.debug("k: %i, Pr[k-j]: %f" % (k,self.Pr[k-j]))
            Quh = Quh + self.UH1[j]*self.Pr[k-j]
            j = j + 1
        return Quh
    
    def setParameters(
        self,
        parameters : Union[list,tuple] = []
        ) -> None:
        """
        Setter for self.parameters.

        Parameters:
        -----------
        parameters : list or tuple

            GRP parameters to set (X0,X1,X2,X3)
        """
        super().setParameters(parameters)
        self.UH1, self.SH1 = GRPProcedureFunction.createUnitHydrograph(self.X3, self.alpha)
    
    def setInitialStates(self,states:Union[list,tuple]=[]):
        """
        Setter for self.initial_states.

        Parameters:
        states : list or tuple

            GRP initial states to set (Sk,Rk)
        """
        super().setInitialStates(states)
