import logging
from typing import Optional, List
from pydrodelta.series_data import SeriesData
from pandas import DataFrame, Series, concat
from math import sqrt
from typing import Union, Tuple
import numpy as np

from ..procedure_function import ProcedureFunctionResults
from ..procedures.pq import PQProcedureFunction
from ..util import interval2timedelta
from ..validation import getSchemaAndValidate
from ..model_parameter import ModelParameter
from ..model_state import ModelState
from ..descriptors.float_descriptor import FloatDescriptor
from ..descriptors.list_descriptor import ListDescriptor
from ..descriptors.dataframe_descriptor import DataFrameDescriptor

class ParFg():
    """Flood guidance parameters"""
    def __init__(
        self,
        parameters : dict,
        area : float = None
        ):
        """
        parameters : dict

            Properties:
            - CN2  
            - hp1dia
            - hp2dias
            - Qbanca

        area : float = None
        """
        self.CN2 = parameters["CN2"]
        """Curve number"""
        self.hp1dia = parameters["hp1dia"]
        self.hp2dias = parameters["hp2dias"]
        self.Qbanca = parameters["Qbanca"]
        self.CN1 = 4.2 * self.CN2 / (10 - 0.058 * self.CN2)
        self.CN3 = 23 * self.CN2 / (10 + 0.13 * self.CN2)
        self.hp1dia = self.hp1dia * area/1000/1000 if area is not None else self.hp1dia
        self.hp2dias = self.hp2dias * area/1000/1000 if area is not None else self.hp2dias

class SmTransform():
    """Soil moisture linear transformation parameters"""
    def __init__(
        self,
        parameters: list
        ):
        """
        parameters : list or tuple: [slope, intercept] """
        self.slope = parameters[0]
        """slope"""
        self.intercept = parameters[1]
        """intercept"""
    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "slope": self.slope,
            "intercept": self.intercept
        }

class SacramentoSimplifiedProcedureFunction(PQProcedureFunction):
    """Simplified (10-parameter) Sacramento for precipitation - discharge transformation. 
    
    Reference: https://www.researchgate.net/publication/348234919_Implementacion_de_un_procedimiento_de_pronostico_hidrologico_para_el_alerta_de_inundaciones_utilizando_datos_de_sensores_remotos"""
    _parameters = [
            #  id  | model_id | nombre | lim_inf | range_min | range_max | lim_sup  | orden 
            # -----+----------+--------+---------+-----------+-----------+----------+-------
        ModelParameter(name="x1_0",constraints=(1,35,200,np.inf)),
            #  229 |       27 | x1_0   |       1 |        35 |       200 | Infinity |     1
        ModelParameter(name="x2_0",constraints=(1,33,248,np.inf)),
            #  230 |       27 | x2_0   |       1 |        33 |       248 | Infinity |     2
        ModelParameter(name="m1",constraints=(1e-09,1,3,np.inf)),
            #  231 |       27 | m1     |   1e-09 |         1 |         3 | Infinity |     3
        ModelParameter(name="c1",constraints=(1e-09,0.01,0.03,np.inf)),
            #  232 |       27 | c1     |   1e-09 |      0.01 |      0.03 | Infinity |     4
        ModelParameter(name="c2",constraints=(1e-09,150,500,np.inf)),
            #  233 |       27 | c2     |   1e-09 |       150 |       500 | Infinity |     5
        ModelParameter(name="c3",constraints=(1e-09,0.00044,0.002,np.inf)),
            #  234 |       27 | c3     |   1e-09 |   0.00044 |     0.002 | Infinity |     6
        ModelParameter(name="mu",constraints=(1e-09,0.4,6,np.inf)),
            #  235 |       27 | mu     |   1e-09 |       0.4 |         6 | Infinity |     7
        ModelParameter(name="alfa",constraints=(1e-09,0.2,0.3,np.inf)),
            #  236 |       27 | alfa   |   1e-09 |       0.2 |       0.3 | Infinity |     8
        ModelParameter(name="m2",constraints=(1e-09,1,2.2,np.inf)),
            #  237 |       27 | m2     |   1e-09 |         1 |       2.2 | Infinity |     9
        ModelParameter(name="m3",constraints=(1e-09,1,5,np.inf))
            #  238 |       27 | m3     |   1e-09 |         1 |         5 | Infinity |    10
    ]

    _states = [
        #  id | model_id | nombre | range_min | range_max | def_val | orden 
        # ----+----------+--------+-----------+-----------+---------+-------
        ModelState(name="x1",constraints=(0,np.inf),default=0),
        #  35 |       27 | x1     |         0 |  Infinity |       0 |     1
        ModelState(name="x2",constraints=(0,np.inf),default=0),
        #  36 |       27 | x2     |         0 |  Infinity |       0 |     2
        ModelState(name="x3",constraints=(0,np.inf),default=0),
        #  37 |       27 | x3     |         0 |  Infinity |       0 |     3
        ModelState(name="x4",constraints=(0,np.inf),default=0)
        #  38 |       27 | x4     |         0 |  Infinity |       0 |     4
    ]

    @property
    def x1_0(self) -> float:
        """top soil layer storage capacity [L]"""
        return self.parameters["x1_0"]
    
    @property
    def x2_0(self) -> float:
        """bottom soil layer storage capacity [L]"""
        return self.parameters["x2_0"]
    
    @property
    def m1(self) -> float:
        """runoff function exponent [-]"""
        return self.parameters["m1"]
    
    @property
    def c1(self) -> float:
        return self.parameters["c1"]
        """interflow function coefficient [1/T]"""
        
    @property
    def c2(self) -> float:
        """percolation function coefficient [-]"""
        return self.parameters["c2"]
    
    @property
    def c3(self) -> float:
        """base flow recession rate [1/T]"""
        return self.parameters["c3"]
    
    @property
    def mu(self) -> float:
        """base flow/deep percolation partition parameter [-]"""
        return self.parameters["mu"]
    
    @property
    def alfa(self) -> float:
        """linear reservoir coefficient [1/T]"""
        return self.parameters["alfa"]
    
    @property
    def m2(self) -> float:
        """percolation function exponent [-]"""
        return self.parameters["m2"]
    
    @property
    def m3(self) -> float:
        """evapotranspiration function exponent [-]"""
        return self.parameters["m3"]

    @property
    def windowsize(self) -> int:
        """Window size for soil moisture adjustment"""
        return self.extra_pars["windowsize"] if "windowsize" in self.extra_pars else None
    
    @property
    def dt_sec(self) -> int:
        """Time step in seconds"""
        return interval2timedelta(self.extra_pars["dt"]).total_seconds() if "dt" in self.extra_pars else 24*60*60
    
    @property
    def rho(self) -> float:
        """Soil porosity"""
        return self.extra_pars["rho"] if "rho" in self.extra_pars else 0.5
    
    @property
    def ae(self) -> float:
        """Effective area of runnof generation [0-1]"""
        return self.extra_pars["ae"] if "ae" in self.extra_pars else 1
    
    @property
    def wp(self) -> float:
        """Wilting point"""
        return self.extra_pars["wp"] if "wp" in self.extra_pars else 0.03
    
    @property
    def sm_transform(self) -> SmTransform:
        """soil moisture rescaling parameters (scale, bias)"""
        return SmTransform(self.extra_pars["sm_transform"]) if "sm_transform" in self.extra_pars else SmTransform([1,0])

    x = ListDescriptor()
    
    @property
    def par_fg(self) -> dict:
        """Flood guidance parameters"""
        return ParFg(self.extra_pars["par_fg"],self.area) if "par_fg" in self.extra_pars else None
    
    @property
    def max_npasos(self) -> int:
        """Maximum substeps for model computations"""
        return self.extra_pars["max_npasos"] if "max_npasos" in self.extra_pars else None

    @property
    def no_check1(self) -> bool:
        """Perform step subdivision based on precipitation intensity nsteps = pma/2  (for numerical stability)"""
        return self.extra_pars["no_check1"] if "no_check1" in self.extra_pars else False
    @no_check1.setter
    def no_check1(self,value : bool) -> None:
        self.extra_pars["no_check1"] = bool(value)
    
    @property
    def no_check2(self) -> bool:
        """Perform step subdivision based on states derivatives (for numerical stability)"""
        return self.extra_pars["no_check2"] if "no_check2" in self.extra_pars else False
    @no_check2.setter
    def no_check2(self,value : bool) -> None:
        self.extra_pars["no_check2"] = bool(value)
    
    @property
    def rk2(self) -> bool:
        """Use Runge-Kutta-2 instead of Runge-Kutta-4"""
        return self.extra_pars["rk2"] if "rk2" in self.extra_pars else False

    volume = FloatDescriptor()
    """Water balance"""    

    _denom_rk = (2,2,1)
    """Runge-Kutta denominators"""
    
    _statenames = ['x1','x2','x3','x4']
    """Model state names"""

    sm_obs = ListDescriptor()
    """Soil moisture observations"""

    sm_sim = ListDescriptor()
    """Simulated soil moisture"""

    results = DataFrameDescriptor()
    """Procedure results"""

    X = ListDescriptor()
    """Runge-Kutta derivatives of each substep"""

    Xw = ListDescriptor()
    """Runge-Kutta weigthed derivatives of each substep"""

    flows = DataFrameDescriptor()
    """Mean flows for each substep"""

    @property
    def mock_run(self) -> bool:
        """Perform mock run"""
        return True if "mock_run" in self.extra_pars and bool(self.extra_pars["mock_run"]) else False
    @mock_run.setter
    def mock_run(self,value : bool):
        self.extra_pars["mock_run"] = bool(value)

    _pivot_input : bool = True
    """Set to True if the run method requires a pivoted input"""

    def __init__(
        self,
        parameters : Union[dict,list,tuple],
        initial_states : list,
        **kwargs
        ):
        """
        parameters : Union[dict,list,tuple]
        
            Properties:
            - x1_0 : float
                top soil layer storage capacity [L]
            - x2_0 : float
                bottom soil layer storage capacity [L]
            - m1 : float
                runoff function exponent [-]
            - c1 : float
                interflow function coefficient [1/T]        
            - c2 : float
                percolation function coefficient [-]        
            - c3 : float
                base flow recession rate [1/T]        
            - mu : float
                base flow/deep percolation partition parameter [-]        
            - alfa : float
                linear reservoir coefficient [1/T]        
            - m2 : float
                percolation function exponent [-]        
            - m3
                evapotranspiration function exponent [-]
        
        extra_pars : Union[dict,list,tuple]
        
            - windowsize : int
                Window size for soil moisture adjustment        
            - dt_sec : int
                Time step in seconds        
            - rho : float
                Soil porosity        
            - ae : float
                Effective area of runnof generation [0-1]        
            - wp : float
                Wilting point        
            - sm_transform : tuple
                soil moisture rescaling parameters (scale, bias)
            - par_fg : dict
                Flood guidance parameters
            - max_npasos : int
                Maximum substeps for model computations        
            - no_check1 : bool
                Perform step subdivision based on precipitation intensity nsteps = pma/2  (for numerical stability)        
            - no_check2 : bool
                Perform step subdivision based on states derivatives (for numerical stability)        
            - rk2 : bool
                Use Runge-Kutta-2 instead of Runge-Kutta-4
        
        initial_states : list
        
                Initial model states (x1,x2,x3,x4)
                """
        kwargs["type"] = "SacramentoSimplified"
        super().__init__(
            parameters = parameters, 
            initial_states = initial_states,
            **kwargs) # super(PQProcedureFunction,self).__init__(params,procedure)
        getSchemaAndValidate(dict(kwargs, parameters = parameters, initial_states = initial_states),"SacramentoSimplifiedProcedureFunction")
        self.volume = 0
        self.sm_obs = []
        self.sm_sim = []
        self.x = [self.constraint(self.initial_states[i],self._statenames[i]) for i in range(4)]
        self.X = []
        self.Xw = []
        self.flows = None
    
    def constraint(self,value,name):
        if name == 'x1':
            limsup = self.x1_0
            flag = True
        elif name == 'x2':
            limsup = self.x2_0
            flag = True
        else:
            flag = False
        return max(0,min(value,limsup) if flag else value)

    def computeFloodGuidance(self,x,Qcurrent):
        if Qcurrent < self.par_fg.Qbanca:
            Th_R1 = (self.par_fg.Qbanca - Qcurrent) / self.par_fg.hp1dia * 3.6
            Th_R2 = (self.par_fg.Qbanca - Qcurrent) / self.par_fg.hp2dias * 3.6
            CN = self.par_fg.CN1 + (self.par_fg.CN3 - self.par_fg.CN1) * (x[0] + x[1]) / (self.x1_0 + self.x2_0)
            S = 25400 / CN - 254
            FG1 = 0.5 * (Th_R1 + 0.4 * S + sqrt((Th_R1 + 0.4 * S)**2 - 4 * (0.04 * S**2 - 0.8 * S * Th_R1)))
            FG2 = 0.5 * (Th_R2 + 0.4 * S+sqrt((Th_R2 + 0.4 * S)**2 - 4 * (0.04 * S**2 - 0.8 * S * Th_R2)))
            return (FG1,FG2)
        return None, None

    def check3(self, x1n, X0, c):
        nn = 1
        if x1n != 0 and x1n + X0 * c < 0:
            nn = 2 + int(1/x1n * c * abs(X0))
        return min(15,nn)

    def check2(self, x2, x2_0, x1):
        if x2 < 0:
            return (int(2 - x2 / x2_0 * 2), 1)
        elif x2 > x2_0:
            return (int( 2 + (x2 - x2_0) / x2_0 * 2), 1)
        elif x1 < 0:
            return (int(2 - x1 * 10), 1)
        else:
            return (1, 0)

    def check(self,x0,x1,pma,etp):
        n1 = 1
        n2 = 1
        x1n = x0
        x2n = x1
        p = pma
        pet = etp
        x1 = x1n
        x2 = x2n
        X = [list() for i in range(4)]
        rk = 0
        while rk <= 3:
            sr = p * (x1 / self.x1_0)**self.m1
            pc = self.c3 * self.x2_0 * (1 + self.c2*(1 - x2 / self.x2_0)**self.m2) * (x1 / self.x1_0)
            et1 = pet * (x1 / self.x1_0)
            int = self.c1 * x1
            et2 = (pet - et1) * (x2 / self.x2_0)**self.m3
            gw = self.c3 * x2
            bf = (1 + self.mu)**(-1) * gw + int
            X[rk].append(p - sr - pc - et1 - int)
            X[rk].append(pc - et2 - gw)
            X[rk].append(sr + bf)
            if(rk<3):
                n1 = max(n1,self.check3(x1n,X[rk][0],1 / self._denom_rk[rk]))
            (n, fl) = self.check2(x2, self.x2_0, x1)
            n2 = max(n, n2)
            rk = 3 if fl == 1 else rk
            if(rk < 3):
                x1 = self.constraint(x1n + X[rk][0] / self._denom_rk[rk],'x1')
                x2 = self.constraint(x2n + X[rk][1] / self._denom_rk[rk],'x2')
            rk = rk + 1
        return (n1, n2)

    def advance_substep(self, x_n, p, pet, npasos, step, substep : int):
        x_ = x_n.copy()            # @x_n: estados iniciales @x_: estados intermedios
        X = [list() for i in range(4)]                   # @X: derivadas
        flows = []
        for rk in range(4):
            sr = p * (x_[0] / self.x1_0)**self.m1
            et1 = pet * (x_[0] / self.x1_0)
            int = self.c1 * x_[0]
            pc = self.c3 * self.x2_0 * (1 + self.c2*(1 - x_[1] / self.x2_0)**self.m2) * (x_[0] / self.x1_0)
            et2 = (pet - et1) * (x_[1] / self.x2_0)**self.m3
            gw = self.c3 * x_[1]
            bf = (1 + self.mu)**(-1) * gw + int
            X[rk].append(p - sr - pc - et1 - int)
            X[rk].append(pc - et2 - gw)
            X[rk].append(sr + bf - x_[2] * self.alfa)
            X[rk].append(x_[2] * self.alfa - x_[3] * self.alfa)
            deep_perc = self.c3 * x_[1] * (1 - (1 + self.mu)**(-1) )
            flows.append((rk, p, sr, et1, int, pc, et2, gw, bf, x_[2] * self.alfa, x_[3] * self.alfa, deep_perc))
            # rk = rk + 1
            # sr = p * (x_[0] / self.x1_0) ** self.m1
            # et1 = pet * (x_[0] / self.x1_0)
            # int = self.c1 * x_[0]
            # pc = self.c3 * self.x2_0 * (1 + self.c2 * ( 1 - x_[1] / self.x2_0) ** self.m2) * (x_[0] / self.x1_0)
            # #~ $pc = ($pc/$_[6] > $x_[0] + ($p + $sr - $et1 - $int)/$_[6]) ? $x_[0] + ($p + $sr - $et1 - $int)/$_[6] : $pc;
            # ### min($c3*$x2_0*(1+$c2*(1-$x_[1]/$x2_0)**$m2)*($x_[0]/$x1_0),$x_[0]+$p/$npasos-$sr/$npasos-$et1/$npasos-$int/$npasos);
            # et2 = (pet - et1) * (x_[1] / self.x2_0) ** self.m3
            # gw = self.c3 * x_[1]
            # bf = (1 + self.mu) ** (-1) * gw + int
            # X[rk][0] = p - sr - pc - et1 - int
            # X[rk][1] = pc - et2 - gw
            # X[rk][2] = sr + bf - x_[2] * self.alfa
            # X[rk][3] = x_[2] * self.alfa - x_[3] * self.alfa
            # printf $rk_out "%s    %.2f    %d    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f\n",  $gl_date, $gl_mjd, $rk, $p, $pet, $x_[0], $x_[1], $x_[2], $x_[3], $sr, $et1, $int, $pc, $et2, $gw, $bf, $X[$rk][0],  $X[$rk][1],  $X[$rk][2],  $X[$rk][3];
            ### if rk2
            if self.rk2:
                if rk == 0:
                    for i in range(4):
                        x_[i] = self.constraint(x_n[i] + X[rk][i]/npasos,self._statenames[i])         
                else:
                    out = []
                    Xw = []
                    for k in range(4):
                        Xw_ = (X[0][k] + X[1][k]) / 2 / npasos
                        out.append(self.constraint(x_n[k] + Xw_, self._statenames[k]))
                        Xw.append(Xw_)
                    self.X.append(X)
                    self.Xw.append(Xw)
                    self.flows.loc[len(self.flows)] = [step, substep, 1 / npasos, *self.computeMeanFlows(flows, x_n, 2), *x_n, *Xw]
                    #~ @x = @out;
                    return [out[0], out[1], out[2], out[3]]
                #~ last;
            else:    #### rk4
                if rk < 3:
                    for i in range(4):
                        x_[i] = self.constraint(x_n[i] + X[rk][i] / self._denom_rk[rk]/npasos,self._statenames[i])
                else:
                    out = []
                    max = (self.x1_0,self.x2_0)
                    Xw = []
                    for k in range(4):
                        Xw_ = (X[0][k] + 2 * X[1][k] + 2 * X[2][k] + X[3][k]) / 6 / npasos
                        out.append(self.constraint(x_n[k] + Xw_, self._statenames[k]))
                        Xw.append(Xw_)
                    self.X.append(X)
                    self.Xw.append(Xw)
                    self.flows.loc[len(self.flows)] = [step, substep, 1 / npasos, *self.computeMeanFlows(flows, x_n, 4), *x_n, *Xw]
                    return [out[0], out[1], out[2], out[3]]


    def advance_step(self,x : List[float],pma,etp, step):
        x_ = x.copy()
        if not self.no_check1:
            npasos = max(1,int(pma/2))
        else:
            npasos = 1
        n1 = 1
        n2 = 1
        maxn = self.max_npasos if self.max_npasos is not None else 24
        if not self.no_check2:
            (n1, n2) = self.check(x_[0],x_[1],pma,etp)
        npasos = max(n2, max(npasos, min(24, n1)))
        npasos = npasos if self.max_npasos is None else min(self.max_npasos, npasos)
        l = 1
        while(l <= npasos):
            # gl_mjd += 1/npasos
            x_ = self.advance_substep(x_, pma, etp, npasos, step, l - 1)
            # printf $super_out "%s    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f\n", $gl_date, $gl_mjd, $_[4]/$npasos, $_[5]/$npasos, @x;
            l = l + 1

        return x_, npasos

    def run(self,input: Optional[DataFrame]=None) -> Tuple[List[SeriesData], ProcedureFunctionResults]:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        """
        if input is None:
            input = self._procedure.loadInput(
                inplace=False,
                pivot=True,
                use_boundary_name=True,
                tag_column=False)
        # results = DataFrame({
        #     "timestart": Series(dtype='datetime64[ns]'),
        #     "pma": Series(dtype='float'),
        #     "etp": Series(dtype='float'),
        #     "q_obs": Series(dtype='float'),
        #     "smc_obs": Series(dtype='float'),
        #     "x0": Series(dtype='float'),
        #     "x1": Series(dtype='float'),
        #     "x2": Series(dtype='float'),
        #     "x3": Series(dtype='float'),
        #     "q3": Series(dtype='float'),
        #     "q4": Series(dtype='float'),
        #     "smc": Series(dtype='float'),
        #     "k": Series(dtype='int'),
        #     "fg1": Series(dtype='float'),
        #     "fg2": Series(dtype='float'),
        #     "substeps": Series(dtype='int')
        # })
        # results.set_index("timestart", inplace=True)
        # initialize states
        self.x = [self.constraint(self.initial_states[i],self._statenames[i]) for i in range(4)]
        step = 0
        self.flows = DataFrame(columns = ["step", "substep", "substep_duration", "p", "sr", "et1", "int", "pc", "et2", "gw", "bf", "q2", "q3","deep_perc", "x1", "x2", "x3", "x4", "X1", "X2", "X3", "X4"])

        # series: pma*, etp*, q_obs, smc_obs [*: required]
        if len(input) < 2:
            raise Exception("Missing input series: at least pma and etp required")
        # instantiate lists for statistics computation
        sim = []
        obs = []
        sm_obs = []
        sm_sim = []
        k = -1
        result_rows = []
        # iterate series using pma's index:
        for i, row in input.iterrows():
            k = k + 1
            pma = row["pma"]
            etp = row["etp"] # input[1].loc[[i]].valor.item()
            q_obs = row["q_obs"] # input[2].loc[[i]].valor.item() if len(input) > 2 else None
            smc_obs = row["smc_obs"] # input[3].loc[[i]].valor.item() if len(input) > 3 else None

            if self.mock_run:
                result_rows.append([i, pma, etp, q_obs, smc_obs, self.x[0], self.x[1], self.x[2], self.x[3], 0, 0, 0, k, 0, 0, 1])
                sim.append(0)
                obs.append(0)
                continue

            smc = (self.rho - self.wp) * self.x[0] / self.x1_0 + self.wp

            if np.isnan(pma):
                if self.fill_nulls:
                    logging.warning("Missing pma value for date: %s. Filling up with 0" % i)
                    pma = 0
                else:
                    logging.warning("Missing pma value for date: %s. Unable to continue" % i)
                    break
            if etp is None:
                if self.fill_nulls:
                    logging.warning("Missing etp value for date: %s. Filling up with 0" % i)
                    etp = 0
                else:
                    logging.warning("Missing etp value for date: %s. Unable to continue" % i)
                    break
            # calculate fluxes at the beggining of the step 
            q3 = self.area * self.alfa * self.x[2] / 1000 / self.dt_sec * self.ae
            q4 = self.area * self.alfa * self.x[3] / 1000 / self.dt_sec * self.ae
            deep_perc = self.c3 * self.x[1] * (1 - (1 + self.mu)**(-1) )
            real_et = etp * (self.x[0] / self.x1_0  + (1 - self.x[0] / self.x1_0) * (self.x[1] / self.x2_0)**self.m3)
            smcsim = (self.rho - self.wp) * self.x[0] / self.x1_0 + self.wp
            gl_date = i
            q_ = q_obs
            sm_ = min(max(smc,self.wp),self.rho) if smc is not None else None
            sm_obs.append(sm_)
            sm_sim.append(smcsim)
            # flood guidance
            if self.par_fg is not None:
                Qcurrent = q_ if q_ is not None else q4
                (fg1, fg2) = self.computeFloodGuidance(self.x,Qcurrent)
            else:
                fg1 = None
                fg2 = None

            # new_row = DataFrame([[i, pma, etp, q_obs, smc_obs, x[0], x[1], x[2], x[3], q3, q4, smcsim, k, fg1, fg2, None]], columns= ["timestart", "pma", "etp", "q_obs", "smc_obs", "x0", "x1", "x2", "x3", "q3", "q4", "smc", "k", "fg1", "fg2","substeps"])
            
            #advance step
            x_0 = self.x.copy()
            (self.x, npasos) = self.advance_step(self.x,pma,etp, i)
            # new_row.loc[[0],'substeps'] = npasos
            
            # write row
            result_rows.append([i, pma, etp, q_obs, smc_obs, x_0[0], x_0[1], x_0[2], x_0[3], q3, q4, smcsim, k, fg1, fg2, npasos, deep_perc, real_et])
            if q_obs is not None:
                sim.append(q4)
                obs.append(q_obs)
        
        results = DataFrame(result_rows, columns= ["timestart", "pma", "etp", "q_obs", "smc_obs", "x0", "x1", "x2", "x3", "q3", "q4", "smc", "k", "fg1", "fg2","substeps","deep_perc","real_et"])
        results.set_index("timestart", inplace=True)
        # results = concat(result_rows).set_index("timestart")
        # logging.debug(str(results))
        procedure_results = ProcedureFunctionResults(
            border_conditions = results[["pma","etp","q_obs","smc_obs"]],
            initial_states = self.initial_states,
            states = results[["x0","x1","x2","x3"]],
            parameters = self.parameters,
            extra_pars = {
                "rho": self.rho,
                "area": self.area,
                "ae": self.ae,
                "wp": self.wp,
                "sm_transform": self.sm_transform.toDict(),
                "par_fg": self.par_fg,
                "max_npasos": self.max_npasos,
                "no_check1": self.no_check1,
                "no_check2": self.no_check2,
                "rk2": self.rk2,
                "dt_sec": self.dt_sec
            },
            # "statistics": {
            #     "obs": obs,
            #     "sim": sim,
            #     "compute": True
            # },
            data = results    
        )
        self.results = results
        return (
            [results[["q4"]].rename(columns={"q4":"valor"}),results[["smc"]].rename(columns={"smc":"valor"})],
            procedure_results
        )

    def setParameters(
        self, 
        parameters: Union[list,tuple] = ...) -> None:
        super().setParameters(parameters)
    
    def setInitialStates(
        self, 
        states: Union[list,tuple] = ...) -> None:
        super().setInitialStates(states)
    
    def massBalance(self) -> dict:
        if self.results  is None or not len(self.results):
            raise ValueError("Can't compute mass balance: results not found")
        integrated_flows = self.integrateFlows()
        r = {
            **integrated_flows,
            "initial_storage": sum(self.initial_states),
            "final_storage":  sum(self.x),
        }
        r["mass_balance"] = r["p"] - r["et1"] - r["et2"] - r["q3"] - r["deep_perc"]
        r["storage_difference"] = r["final_storage"] - r["initial_storage"]
        r["discrepancy"] = r["mass_balance"] - r["storage_difference"]
        r["discrepancy_per_step"] = r["discrepancy"] / len(self.results)
        r["discrepancy_as_fraction_of_input"] = r["discrepancy"] / r["p"]
        r["runoff_coefficient"] = r["q3"] / r["p"]
        return r
        
    def computeMeanFlows(self,flows_, x_n, rk):
        flows = DataFrame(flows_, columns=["rk", "p", "sr", "et1", "int", "pc", "et2", "gw", "bf", "q2", "q3", "deep_perc"])
        mean_flows = []
        for key in ["p", "sr", "et1", "int", "pc", "et2", "gw", "bf", "q2", "q3", "deep_perc"]:
            if rk == 2:
                mean = flows[key].sum() / len(flows)
            else:
                mean = flows.apply(
                    lambda row: row[key] * (2 if row["rk"] in [1,2] else 1),
                    axis=1
                ).sum() / 6
            mean_flows.append(mean)
        return mean_flows
    
    def integrateFlows(self):
        if self.flows is None:
            raise Exception("Can´t integrate flows, flows property is None. Run the procedure to generate flows.")
        results = {}
        for key in ["p", "sr", "et1", "int", "pc", "et2", "gw", "bf", "q2", "q3", "deep_perc"]:
            results[key] = self.flows.apply(
                lambda row: row[key] * row["substep_duration"],
                axis=1
            ).sum()
        return results