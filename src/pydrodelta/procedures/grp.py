import logging
from numpy import tanh
# from typing import Optional
# from pydrodelta.series_data import SeriesData
from pandas import DataFrame, Series, concat
from typing import Union
from numpy import inf, isnan

from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.model_parameter import ModelParameter
from pydrodelta.model_state import ModelState
from .pq import PQProcedureFunction

class GRPProcedureFunction(PQProcedureFunction):

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

    def __init__(
        self,
        update = False,
        **kwargs):
        """
        Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
        Guarda procedure en self._procedure (procedimiento al cual pertenece la función)
        """
        # logging.debug("Running GRPProcedureFunction constructor")
        super().__init__(**kwargs) # super(PQProcedureFunction,self).__init__(params,procedure)
        self.X0  : float = self.parameters["X0"]
        """X0	capacite du reservoir de production (mm)"""
        self.X1  : float = self.parameters["X1"]
        """X1	capacite du reservoir de routage (mm)"""
        self.X2  : float = self.parameters["X2"]
        """X2	facteur de l'ajustement multiplicatif de la pluie efficace(sans dimension)"""
        self.X3  : float = self.parameters["X3"]
        """X3	temps de base de l'hydrogramme unitaire (d)"""
        self.windowsize  : int = self.extra_pars["windowsize"] if "windowsize" in self.extra_pars else None
        """time window size"""
        self.rho  : float = self.extra_pars["rho"] if "rho" in self.extra_pars else 0.5
        """rho soil porosity [0-1]"""
        self.wp  : float = self.extra_pars["wp"] if "wp" in self.extra_pars else 0.03
        """wp soil wilting point [0-1]"""
        self.ae  : float = self.extra_pars["ae"] if "ae" in self.extra_pars else 1
        """ae effective area [0-1]"""
        self.Sk_init : float  = self.initial_states["Sk"] if "Sk" in self.initial_states else 0
        """initial soil storage"""
        self.Rk_init : float = self.initial_states["Rk"] if "Rk" in self.initial_states else 0
        """initial routing storage"""
        self.dt : float = 1
        """computation step of the unit hydrograph"""
        self.alpha : float = 5/2
        """exponent of the unit hydrograph"""
        self.UH1, self.SH1 = GRPProcedureFunction.createUnitHydrograph(self.X3, self.alpha)
        """Unit hydrograph"""
        self.update : bool = update
        """Update states with observed discharge"""
    @staticmethod
    def createUnitHydrograph(
        X3 : float,
        alpha : float
        ) -> tuple:
        """Creates unit hydrograph
        
        Parameters:
        -----------
        X3 : float
            Unit hydrograph base time
        
        alpha : float
            Unit hydrograph exponent
        
        Returns:
        --------
        2-tuple : where first element is the pulses Unit hydrograph and the second is the accumulated unit hydrograph"""
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

    # def run(self,input: Optional[List[SeriesData]]=None) -> Tuple[List[SeriesData], ProcedureFunctionResults]:
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
            Boundary conditions. If None, runs .loadInput

        Returns:
        2-tuple : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object
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
                if self.fillnulls:
                    logging.warn("Missing pma value for date: %s. Filling up with 0" % i)
                    pma = 0
                else:
                    logging.warn("Missing pma value for date: %s. Unable to continue" % i)
                    break
            if isnan(etp):
                if self.fillnulls:
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
        ) -> tuple:
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
        tuple : (Sk_, Rk_, Qk, Qr, self.X2*(Perc+Pn-Ps), R1 - R1**2/(R1+self.X1)"""
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
        float"""

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
        self.X0 = self.parameters["X0"]
        self.X1 = self.parameters["X1"]
        self.X2 = self.parameters["X2"]
        self.X3 = self.parameters["X3"]
        self.UH1, self.SH1 = GRPProcedureFunction.createUnitHydrograph(self.X3, self.alpha)
    
    def setInitialStates(self,states:Union[list,tuple]=[]):
        """
        Setter for self.initial_states.

        Parameters:
        states : list or tuple
            GRP initial states to set (Sk,Rk)
        """
        super().setInitialStates(states)
        self.Sk_init = self.initial_states["Sk"]
        self.Rk_init = self.initial_states["Rk"]
