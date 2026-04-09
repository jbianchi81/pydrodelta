import logging
from typing import Optional, List, Tuple, Union, Literal, TypedDict, cast, NamedTuple
from ..series_data import SeriesData
import numpy as np 
from pandas import DataFrame, Series, concat, Timestamp
from datetime import datetime
from ..util import get_stats, StatsDict

from ..procedure_function import ProcedureFunctionResults
import pydrodelta.procedures.sacramento_simplified as sac

from ..descriptors.list_descriptor import ListDescriptor

class AsimParsDict(TypedDict, total=False):
    p_stddev : float
    pet_stddev : float
    x_stddev : float
    var_innov : List[Union[float,Literal["reg","rule"]]]
    trim_sm : List[bool]
    rule : List[List[float]]
    asim : List[Literal["smc","q"]]
    update : List[Literal["x1","x2","x3","x4"]]
    xpert : bool
    replicates : int
    stddev_forzantes: List[float]

class Asim(NamedTuple):
    sm : bool
    q : bool

class Update(NamedTuple):
    x1 : bool
    x2 : bool
    x3 : bool
    x4 : bool

class StddevForzantes(NamedTuple):
    p: float
    pet: float

class VarInnov(NamedTuple):
    sm : Union[Literal["reg","rule"],float]
    q : Union[Literal["reg","rule"],float]

class TrimSm(NamedTuple):
    lower: bool
    upper: bool

class RqRule(NamedTuple):
    is_greater_than : float
    var : float
    bias : float

class SacEnkfProcedureFunction(sac.SacramentoSimplifiedProcedureFunction):
    """Simplified (10-parameter) Sacramento for precipitation - discharge transformation - ensemble with data assimilation. 
    
    Reference: https://www.researchgate.net/publication/348234919_Implementacion_de_un_procedimiento_de_pronostico_hidrologico_para_el_alerta_de_inundaciones_utilizando_datos_de_sensores_remotos"""

    _kalman_def = {
        "stddev_forzantes": StddevForzantes(0.25,0.1),
        "x_stddev": 0.15,
        "var_innov": VarInnov(0.03,"rule"),
        "trim_sm": TrimSm(False,True),
        "asim": Asim(False,True),
        "update": Update(True, True, True, True),
        "xpert": True,
        "sm_transform": (1,0),
        "replicates": 35,
        "windowsize": 1,
    }

    asim_pars : AsimParsDict

    @property
    def stddev_forzantes(self) -> StddevForzantes:
        """Standard deviation of the error of inputs"""
        if "stddev_forzantes" in self.asim_pars:
            return StddevForzantes(*self.asim_pars["stddev_forzantes"]) 
        else:
            return self._kalman_def["stddev_forzantes"]

    @property
    def p_stddev(self) -> float:
        """Standard deviation of the error of input precipitation"""
        return self.stddev_forzantes[0]

    @property
    def pet_stddev(self) -> float:
        """Standard deviation of the error of input potential evapotranspiration"""
        return self.stddev_forzantes[1]

    @property
    def x_stddev(self) -> float:
        """Standard deviation of the model states"""
        return self.asim_pars['stddev_estados'] if "stddev_estados" in self.asim_pars else self._kalman_def["x_stddev"]

    @property
    def var_innov(self) -> VarInnov:
        """variance of the innovations (observation error): soil moisture (first element) and discharge (second element). If second element is 'rule', get variance of discharge from the rule defined in self.Rqobs"""
        if "var_innov" in self.asim_pars:
            return VarInnov(self.asim_pars["var_innov"][0],self.asim_pars["var_innov"][1]) 
        else:
            return self._kalman_def["var_innov"]

    @property
    def trim_sm(self) -> TrimSm:
        """2-tuple of bool. Option to trim soil moisture observations at the low (wilting point, self.wf) and high (soil porosity, self.rho) values, respectively"""
        if "trim_sm" in self.asim_pars:
            return TrimSm(self.asim_pars["trim_sm"][0],self.asim_pars["trim_sm"][0])
        else:
            return self._kalman_def["trim_sm"]

    @property
    def Rqobs(self) -> List[RqRule]:
        """Rule to determine observed discharge error variance as a function of the observed value. Ordered list of (threshold, bias, variance)"""
        if self.var_innov[1] == "rule":
            if "rule" not in self.asim_pars:
                raise Exception("Missing parameter 'rule'")
            return [RqRule(*r) for r in self.asim_pars["rule"]]
        else:
            return [RqRule(0,float(self.var_innov[0]),0)]

    @property
    def asim(self) -> Asim:
        """Option to assimilate soil moisture and discharge, respectively"""
        if "asim" in self.asim_pars:
            return Asim("sm" in self.asim_pars["asim"], "q" in self.asim_pars["asim"])
        else:
            return self._kalman_def["asim"]

    @property
    def update(self) -> Update:
        """4-tuple of bool. Option to correct model states via data assimilation (x1, x2, x3, x4) """
        if "update" in self.asim_pars:
            return Update(
                "x1" in self.asim_pars["update"],
                "x2" in self.asim_pars["update"],
                "x3" in self.asim_pars["update"],
                "x4" in self.asim_pars["update"]
            )
        else:
            return self._kalman_def["update"]

    @property
    def xpert(self) -> bool:
        """Option to add noise to model states at the beginning of each step"""
        return self.asim_pars["xpert"] if "xpert" in self.asim_pars else self._kalman_def["xpert"]

    @property
    def replicates(self) -> int:
        """Number of ensemble members"""
        return self.asim_pars["replicates"] if "replicates" in self.asim_pars else self._kalman_def["replicates"]

    ens : List[sac.States]
    """Ensemble of model states (length = len(self.replicates) list of 4-tuples)"""

    ens1 : List[sac.States]
    """Ensemble of model states without data assimilation in the last step (length = len(self.replicates) list of 4-tuples)"""
    
    ens2 : List[sac.States]
    """Ensemble of model states without data assimilation in the last 2 steps (length = len(self.replicates) list of 4-tuples)"""
    
    mediassinpert = ListDescriptor()
    
    sm_obs = ListDescriptor()
    
    sm_sim = ListDescriptor()

    H : Optional[List[List[float]]]
    """The states transformation matrix"""

    _pivot_input : bool = False
    """Set to True if the run method requires a pivoted input"""

    def __init__(
        self,
        extra_pars : sac.ExtraParsDict = {},
        asim_pars : AsimParsDict = {},
        **kwargs
        ):
        """
        sim_pars : AsimParsDict = {}
        
            Properties:
            - p_stddev : float - Standard deviation of the error of input precipitation
            - pet_stddev : float - Standard deviation of the error of input potential evapotranspiration
            - x_stddev : float - Standard deviation of the model states
            - var_innov : tuple - variance of the innovations (observation error): soil moisture (first element) and discharge (second element). If second element is 'rule', get variance of discharge from the rule defined in self.Rqobs
            - trim_sm : tuple - 2-tuple of bool. Option to trim soil moisture observations at the low (wilting point, self.wf) and high (soil porosity, self.rho) values, respectively
            - rule : List[Tuple[float,float,float]] - Rule to determine observed discharge error variance as a function of the observed value. Ordered list of (threshold, bias, variance)
            - asim : 2-tuple of str or None - Option to assimilate soil moisture and discharge, respectively
            - update : 4-tuple or str or None - Option to correct model states via data assimilation (x1, x2, x3, x4)
            - xpert : bool - Option to add noise to model states at the beginning of each step
            - replicates : int - Number of ensemble members"""
        super().__init__(extra_pars = extra_pars, **kwargs)
        self.asim_pars = asim_pars
        # self.c1dia = self.c1
        # self.c3dia = self.c3
        # self.alfadia = self.alfa
        self.setH()

        # states
        self.ens = list()
        self.ens1 = list()
        self.ens2 = list()
        self.mediassinpert = list()
        self.sm_obs = list()
        self.sm_sim = list()

    def xnoise(
        self,
        value : float,
        statename : str
        ) -> float:
        """Get product of value with a random normal of mean 0, scale = self.x_stddev

        The result is constrained to the valid range of range the model state variable 
        
        Parameters:
        -----------
        value : float
            Input value of the model state
        
        statename : str
            Name of the model state variable (one of x1, x2, x3, x4)"""
        pert = value * np.random.normal(loc=0,scale=self.x_stddev)
        pert = self.constraint(pert,statename)
        return pert

    def cero(
        self,
        value : float,
        max : float
        ) -> float:
        """Return max(0, min(value, max))
        
        Parameters:
        -----------
        value : float
        
        max : float
        
        Returns:
        --------
        float"""
        if value <0:
            return 0
        elif value > max:
            return max
        else:
            return value

    def get_ens_stats(
        self,
        index : int
        ) -> Tuple[StatsDict,StatsDict,StatsDict]:
        """Get the ensemble stats (mean, min, max, p10, p90) of the model state variable of the selected index for each ensemble (self.ens, self.ens1, self.ens2)
        
        Parameters:
        -----------
        index : 0 <= int <= 3
        
        Returns:
        --------
        stats of ensemble 0 (self.ens) : StatsDict
        stats of ensemble 1 (self.ens1) : StatsDict
        stats of ensemble 2 (self.ens2) : StatsDict"""
        ens0_stats = get_stats([self.ens[i][index] for i in range(self.replicates)])
        ens1_stats = get_stats([self.ens1[i][index] for i in range(self.replicates)])
        ens2_stats = get_stats([self.ens2[i][index] for i in range(self.replicates)])
        return ens0_stats, ens1_stats, ens2_stats

    def media1(
        self,
        index : int
        ) -> float:
        """Get the ensemble mean of the model state variable of the selected index
        
        Parameters:
        -----------
        index : 0 <= int <= 3
        
        Returns:
        --------
        float"""
        sum = 0
        for i in range(self.replicates):
            sum += self.ens[i][index]
        return sum / self.replicates

    def covarianza(
        self,
        index_1 : int,
        index_2 : int
        ) -> float:
        """Get ensemble covariance between model state variables of index_1 and index_2
        
        Parameters:
        -----------
        index_1 : 0 <= int <= 3
        
        index_2: 0 <= int <= 3
        
        Returns:
        --------
        float"""
        sum = 0
        for i in range(self.replicates):
            sum += (self.ens[i][index_1] - self.mediassinpert[index_1]) * (self.ens[i][index_2] - self.mediassinpert[index_2])
        return sum / self.replicates

    def q(
        self,
        value : float
        ) -> Union[Tuple[float,float],Tuple[None,None]]:
        """Get variance and bias for the given value of discharge, according the mapping at self.Rqobs
        
        Parameters:
        -----------
        value :float
        
        Returns:
        --------
        variance : float
        
        bias : float"""
        for R in self.Rqobs:
            # logging.debug("R: %s, value: %s" % (str(R), str(value)))
            if value >= R[0]:
                return R[1], R[2]
        return None, None

    def linfit(
        self,
        wsize : int,
        value : float
        ) -> float:
        """Adjust soil moisture value with a linear regression of the error of simulated vs observed values in a time step window of wsize
        
        Parameters:
        -----------
        wsize : int
        
        value : float
        
        Returns:
        --------
        float"""
        if self.windowsize is None:
            return value
        n = self.windowsize
        sumX = 0
        sumY = 0
        sumXY = 0
        sumX2 = 0
        I = wsize - self.windowsize + 1 if wsize >= self.windowsize - 1 else  0
        for i in range(I,wsize):
            if i < len(self.sm_obs) and self.sm_obs[i] is not None:
                sumX += self.sm_obs[i]
                sumY += self.sm_sim[i]
                sumXY += self.sm_obs[i] * self.sm_sim[i]
                sumX2 += self.sm_obs[i] ** 2
            else:
                n = n - 1
        if n != 0:
            m = (self.windowsize * sumXY - sumX * sumY) / (self.windowsize * sumX2 - sumX ** 2)
            b = (sumY * sumX2 - sumX * sumXY) / (self.windowsize * sumX2 - sumX ** 2)
            return m * value + b
        else:
            return value

    def advance_step_and_pert(
        self,
        x : sac.States,
        pma : float,
        etp : float,
        step : Union[Timestamp, int]
        ) -> Tuple[sac.States,int]:
        """Advance model step and (where self.xpert is set) add noise
        
        Parameters:
        -----------
        x : list
            model states at the beginning of the step [x1,x2,x3,x4]
        
        pma : float
            Mean areal precipitation during the step
        
        etp : float
            Potential evapotranspiration during the step
        
        Returns:
        --------
        x : list
            the model states at the end of the step [x1,x2,x3,x4]
        
        npasos : int
            The number of substeps used for computation
        """
        x, npasos = self.advance_step(x,pma,etp,step)
        # self.xsinpert = list(x)
        if self.xpert:
            x = self.pertX(x)
        return x, npasos
    
    def pertX(
        self,
        x : sac.States
        ) -> sac.States:
        """Add noise to each of x [x1,x2,x3,x4]
        
        Parameters:
        -----------
        x : list
            Model states  [x1,x2,x3,x4]
        
        Returns:
        --------
        States :  (x1,x2,x3,x4)"""

        return sac.States(
            self.xnoise(x[0],'x1'),
            self.xnoise(x[1],'x2'),
            self.xnoise(x[2],'x3'),
            self.xnoise(x[3],'x4')
        )

    def setH(self) -> None:
        """Set transformation matrix .H"""
        self.H = list()
        for i in range(2):
            if self.asim[i]:
                H_row : List[float] = list()
                for j in range(4):
                    if self.update[j]:
                        H_row.append((self.rho - self.wp) / self.x1_0 if i == 0 and j == 0 else self.alfa * self.area/1000/24/60/60 if i == 1 and j == 3 else 0)
                self.H.append(H_row)
        
    def setInitialEnsemble(
        self,
        init_states : list
        ) -> None:
        """Initialize ensembles (self.ens, self.ens1, self.ens2) from initial states and randomization parameter self.x_stddev. 
        
        Parameters:
        -----------
        init_states : list
            Initial states [x1,x2,x3,x4]"""
        self.ens = list()
        self.ens1 = list()
        self.ens2 = list()
        self.sm_sim = list()
        self.sm_obs = list()
        for i in range(self.replicates):
            x1 =  max(0, min(init_states[0] + np.random.normal(0, self.x1_0 * self.x_stddev), self.x1_0))
            x2 =  max(0, min(init_states[1] + np.random.normal(0, self.x2_0 * self.x_stddev), self.x2_0))
            x3 = max(0, init_states[2] + np.random.normal(0, init_states[2] *  self.x_stddev))
            x4 = max(0, init_states[3] + np.random.normal(0, init_states[3] *  self.x_stddev))
            self.ens.append(sac.States(x1,x2,x3,x4)) 
            # printf $ens "%.3f\t",$ens[$i][$j];
            self.ens1.append(sac.States(x1,x2,x3,x4))
            self.ens2.append(sac.States(x1,x2,x3,x4))
            #~ $json_rep[$i] = "{\"id\":$i,\"name\":\"replicate $i\",\"values\":[";
    
    def getC(self) -> list:
        """Generate covariance matrix C
        
        Returns:
        --------
        covariance matrix C : list"""
        C = list()
        # $C="";
        for k in range(len(self.mediassinpert)):
            row = list()
            for l in range(len(self.mediassinpert)):
                row.append(self.covarianza(k,l))
                # $C .= "$C[$k][$l]	";
            # $C .= "\n";
            C.append(row)
        return C
    
    def getR(
        self,
        innov : Asim,
        qvar : Optional[float],
        smc_var : Optional[float]
        ) -> Tuple[List[List[float]],list]:
        """Generate observation error matrix R and adapt transformation matrix H into H_j according to available observations for assimilation

        Parameters:
        -----------
        innov : (bool, bool)
            Which observed variables to assimilate, respectively: soil moisture, discharge

        qvar : float
            variance of discharge

        smc_var : float
            variance of soil moisture

        Returns:
        --------
        R : list
            The error matrix
        
        H_j : list
            The adapted transformation matrix
        """
        if self.H is None:
            raise Exception("H is not set")
        R : List[List[float]] = list()
        H_j : List[List[float]] = list()
        k = 0
        l = 0
        for i in range(2):
            if self.asim[i]:
                if innov[i]:
                    H_j.append(self.H[k])
                    row = list()
                    l = 0
                    for j in range(2):
                        if self.asim[j] is not None:
                            if innov[j]:
                                if k == l:
                                    if self.var_innov[i] == "rule":
                                        if qvar is None:
                                            raise ValueError("qvar is not set")
                                        row.append(qvar)
                                    else:
                                        if self.var_innov[i] == "reg":
                                            if qvar is None:
                                                raise ValueError("smc_var is not set")
                                            row.append(smc_var)
                                        else:
                                            row.append(self.var_innov[k])
                                else:
                                    row.append(0)
                                l = l + 1
                    R.append(row)
                    k = k + 1
        return R, H_j

    def getKG(
        self,
        H_j : list,
        C : list,
        R : list
        ) -> np.ndarray:
        """Calculate Kalman gain matrix
        
        Parameters:
        -----------
        H_j : list
            Adapted transformation matrix
        
        C : list
            states covariance matrix
        
        R : list
            Observation error covariance matrix
            
        Returns:
        --------
        Kalman gain matrix (KG) : numpy.ndarray"""
        # KG_j = list()
        h = np.array(H_j)
        #~ print "h:$h\n";
        c = np.array(C)
        #~ print "c:$c\n";
        # logging.info("R: %s" % str(R))
        r = np.array(R)
        # logging.info("r: %s" % str(r)) #~ print "r:$r\n";
        hT = h.transpose()
        #~ print "hT:$hT\n";
        product1 = np.matmul(c,hT)
        #~ print "product1:$product1\n";
        product2 = np.matmul(h,product1)
        #~ print "product2:$product2\n";
        sum1 = product2 + r
        #~ print "sum1:$sum1\n";
        inverse = np.linalg.inv(sum1)
        #~ print "inverse:$inverse\n";
        KG = np.matmul(product1,inverse)
        return KG
        #~ print "kg:$KG\n";
        # my @KG=split(/\n/,$KG);
        #~ my @KG_j;
        # for k in range(len(KG)):
        #     $KG[$k]=~s/^\s+|\s+$//g;
        #     my @KG_line=split(/\s+/,$KG[$k]);
        #     for($l=0;$l<@KG_line;$l++)
        #     {
        #         $KG_j[$k][$l]=$KG_line[$l];
        #         print $salida_kg "$KG_j[$k][$l]	";
        #     }				
        # }
        # print $salida_kg "\n";

    def asimila(
        self,
        obs : list,
        R : list,
        KG_j : list
        ) -> list:
        """Assimilate available observations
        
        Parameters:
        -----------
        obs : list
            Available observations for data assimilation
        
        R : list
            Observation error covariance matrix
        
        KG_j : list
            Kalman gain matrix
        
        Returns:
        --------
        err : list
            ensemble model error matrix (difference of simulated states with observed states)
        """
        err_sum = list()
        err = list()
        for j in range(self.replicates):
            for k in range(len(obs)):
                m = 0
                z = 0
                for l in range(len(self.ens[0])):
                    if self.update[l]:
                        if self.H is None:
                            raise Exception("H is not set")
                        z += self.H[k][m] * self.ens[j][l]
                        m = m + 1
                err.append(obs[k] + np.random.normal(0, R[k][k] ** 0.5) - z)
                #~ print $salida_innov "$err[$k],";
            m = 0
            updated = list()
            for k in range(len(self.ens[0])):
                z = 0
                if self.update[k]:
                    for l in range(len(obs)):
                        z += KG_j[m][l] * err[l]
                    m = m + 1
                updated.append(self.constraint(self.ens[j][k] + z, self._statenames[k]))
            self.ens2[j] = self.ens1[j]
            self.ens1[j] = self.ens[j]
            self.ens[j] = sac.States(*updated)
        return err

    def resultsDF(self) -> DataFrame:
        """Convert simulation results into a DataFrame"""
        results =  DataFrame({
            "timestart": Series(dtype='datetime64[ns]'),
            "x1": Series(dtype='float'),
            "x2": Series(dtype='float'),
            "x3": Series(dtype='float'),
            "x4": Series(dtype='float'),
            "q4": Series(dtype='float'),
            "smc": Series(dtype='float')
        })
        # results.set_index("timestart", inplace=True)
        return results

    def newResultsRow(
        self,
        timestart : Optional[datetime] = None,
        x1 : Optional[float] = None,
        x2 : Optional[float] = None,
        x3 : Optional[float] = None,
        x4 : Optional[float] = None,
        q4 : Optional[float] = None,
        smc : Optional[float] = None
        ) -> DataFrame:
        """Generate single-row DataFrame from simulation states and outputs"""
        return DataFrame([[timestart, x1, x2, x3, x4, q4, smc]], columns= ["timestart", "x1", "x2", "x3", "x4", "q4", "smc"])

    def run(
        self,
        input : Optional[Union[DataFrame,List[DataFrame]]]=None
        ) -> Tuple[List[DataFrame], ProcedureFunctionResults]:
        init_states = [self.constraint(self.x[i],self._statenames[i]) for i in range(4)]
        self.setInitialEnsemble(init_states)
        x = sac.States(*init_states)
        x_al = sac.States(*init_states)
        denom_rk = (2,2,1)
        
        if input is None:
            if self._procedure is None:
                raise Exception("procedure is not defined")
            input = cast(List[DataFrame],self._procedure.loadInput(inplace=False,pivot=False))
        elif isinstance(input,DataFrame):
            input = [input]
        results = DataFrame({
            "timestart": Series(dtype='datetime64[ns]'),
            "pma": Series(dtype='float'),
            "etp": Series(dtype='float'),
            "q_obs": Series(dtype='float'),
            "smc_obs": Series(dtype='float'),
            "smc_var": Series(dtype='float'),
            "x1": Series(dtype='float'),
            "x2": Series(dtype='float'),
            "x3": Series(dtype='float'),
            "x4": Series(dtype='float'),
            "q3": Series(dtype='float'),
            "q4": Series(dtype='float'),
            "smc": Series(dtype='float'),
            "k": Series(dtype='int'),
            "fg1": Series(dtype='float'),
            "fg2": Series(dtype='float'),
            "q4_min": Series(dtype="float"),
            "q4_h1": Series(dtype="float"),
            "q4_h2": Series(dtype="float"),
            "smc_min": Series(dtype="float"),
            "smc_p10": Series(dtype="float"),
            "smc_p90": Series(dtype="float"),
            "smc_max": Series(dtype="float"),
            "q_min": Series(dtype="float"),
            "q_p10": Series(dtype="float"),
            "q_p90": Series(dtype="float"),
            "q_max": Series(dtype="float")
        })
        results.set_index("timestart", inplace=True)
        results_al = DataFrame({
            "timestart": Series(dtype='datetime64[ns]'),
            "x1": Series(dtype='float'),
            "x2": Series(dtype='float'),
            "x3": Series(dtype='float'),
            "x4": Series(dtype='float'),
            "q4": Series(dtype='float'),
            "smc": Series(dtype='float'),
            "substeps": Series(dtype='int')
        })
        results_al.set_index("timestart", inplace=True)
        results_min = self.resultsDF()
        results_h1 = self.resultsDF()
        results_h2 = self.resultsDF()
        KG_list = list()            

        if len(input) < 2:
            raise Exception("Missing input series: at least pma and etp required")

        k = -1
        # iterate series using pma's index:
        for timestart, row in input[0].iterrows():
            k = k + 1
            pma = row["valor"]
            etp = input[1].loc[[timestart]].valor.item()
            q_obs = float(input[2].loc[[timestart]].valor.item()) if len(input) > 2 else None
            smc_obs = input[3].loc[[timestart]].valor.item() if len(input) > 3 else None
            smc_var = input[4].loc[[timestart]].valor.item() if len(input) > 4 else None
            smc = (self.rho - self.wp) * x[0] / self.x1_0 + self.wp

            innov = dict()
            obs = []
            if smc_obs is not None and self.asim[0]:
                smc_obs = max(smc,self.wp) if self.trim_sm[0] else smc_obs
                smc_obs = min(smc,self.rho) if self.trim_sm[1] else smc_obs
                #		$smc=max(0,min($rho-$wp,$intercept+$slope*log($smc)-$wp));
                smc_obs -= self.wp
                innov['sm'] = True
                obs.append(smc_obs)
            else:
                innov['sm'] = False
            # my ($qvar,$qbias);
            qvar = None
            qbias = None
            if q_obs is not None and ~np.isnan(q_obs) and self.asim[1]:
                qvar, qbias = self.q(q_obs)
                #		$q=$q+$qbias;
                innov['q'] = True
                obs.append(q_obs)
            else:
                innov['q'] = False
            
            ############### calcula media de cada variable de estado  e imprime ####
            sm_al = x_al[0] * (self.rho - self.wp) / self.x1_0 + self.wp
            self.sm_sim.append(sm_al)
            q_al = x_al[3] * self.area * self.alfa / 1000 / 24 / 60 / 60
            q_ = q_obs if q_obs is not None and q_obs != -9999 else None
            sm_ = smc_obs+self.wp if smc_obs is not None and smc_obs != -1 else None
            if pma is None or etp is None:
                raise Exception("pma and/or etp value missing in step %s" % str(row["timestart"]))
            
            self.sm_obs.append(sm_)
            
            q_minx = list()
            j = 0
            new_row_min = self.newResultsRow(cast(Timestamp,timestart))
            new_row_h1 = self.newResultsRow(cast(Timestamp,timestart))
            new_row_h2 = self.newResultsRow(cast(Timestamp,timestart))
            self.mediassinpert = list()
            
            # get stats of each state
            for i in range(4):
                ens_stats, ens1_stats, ens2_stats = self.get_ens_stats(i)
                if self.update[i]:
                    self.mediassinpert.append(ens_stats["mean"])
                    j = j + 1
                new_row_min.loc[[0],self._statenames[i]] = ens_stats["mean"] 
                new_row_h1.loc[[0],self._statenames[i]] = ens1_stats["mean"] 
                new_row_h1.loc[[0],self._statenames[i]] = ens2_stats["mean"] 
                
                if i == 0:
                    new_row_min.loc[[0],"smc"] = ens_stats["mean"] * (self.rho - self.wp) / self.x1_0 + self.wp
                    new_row_h1.loc[[0],"smc"] = ens1_stats["mean"] * (self.rho - self.wp) / self.x1_0 + self.wp 
                    new_row_h2.loc[[0],"smc"] = ens2_stats["mean"] * (self.rho - self.wp) / self.x1_0 + self.wp 
                elif i == 3:
                    q_f = [
                        ens_stats["mean"] * self.alfa * self.area / 1000 / 24 / 60 / 60,
                        ens1_stats["mean"] * self.alfa * self.area / 1000 / 24 / 60 / 60,
                        ens2_stats["mean"] * self.alfa * self.area / 1000 / 24 / 60 / 60
                    ]
                    new_row_min.loc[[0],"q4"] = q_f[0]
                    new_row_h1.loc[[0],"q4"] = q_f[1]
                    new_row_h2.loc[[0],"q4"] = q_f[2]
                    q_minx = list(q_f)
            C = self.getC()
            R, H_j = self.getR(Asim(innov["sm"], innov["q"]),qvar,smc_var) # if qvar is not None else ([], None)
            if len(R) > 0:
                KG_j = self.getKG(H_j,C,R)
                err = self.asimila(obs,R,KG_j.tolist())
            else:
                KG_j = None
            
            KG_list.append({
                "timestart": timestart,
                "KG": KG_j.tolist() if KG_j is not None else None
            })
            
            ######CALCULA SMC Y Q SIMULADOS (PROMEDIO DEL ENSAMBLE)  ###############
            estados_stats : List[StatsDict] = list()
            sim = list()
            errors = list()
            
            for j in range(len(self.ens[0])):
                ens_stats = get_stats([self.ens[i][j] for i in range(self.replicates)])
                estados_stats.append(ens_stats)
            
            estados_prom = [stats["mean"] for stats in estados_stats]
            Q_out_plus = estados_prom[3] * self.alfa * self.area / 1000 / 24 / 60 / 60
            Q3_plus = estados_prom[2] * self.alfa * self.area / 1000 / 24 / 60 / 60
            sm_out_plus = estados_prom[0] * (self.rho - self.wp) / self.x1_0 + self.wp
            sm_min = estados_stats[0]["min"] * (self.rho - self.wp) / self.x1_0 + self.wp
            sm_p10 = estados_stats[0]["p10"] * (self.rho - self.wp) / self.x1_0 + self.wp
            sm_p90 = estados_stats[0]["p90"] * (self.rho - self.wp) / self.x1_0 + self.wp
            sm_max = estados_stats[0]["max"] * (self.rho - self.wp) / self.x1_0 + self.wp
            q_min = estados_stats[3]["min"] * self.alfa * self.area / 1000 / 24 / 60 / 60
            q_p10 = estados_stats[3]["p10"] * self.alfa * self.area / 1000 / 24 / 60 / 60
            q_p90 = estados_stats[3]["p90"] * self.alfa * self.area / 1000 / 24 / 60 / 60
            q_max = estados_stats[3]["max"] * self.alfa * self.area / 1000 / 24 / 60 / 60
            
            ########## fg ##############
            if self.par_fg is not None:
                Qcurrent = q_ if q_ is not None else Q_out_plus
                (fg1, fg2) = self.computeFloodGuidance(sac.States(*estados_prom),Qcurrent)
            else:
                fg1 = None
                fg2 = None


            # write row
            new_row = DataFrame([[timestart, pma, etp, q_obs, smc_obs, smc_var, estados_prom[0], estados_prom[1], estados_prom[2], estados_prom[3], Q3_plus, Q_out_plus, sm_out_plus, k, fg1, fg2, q_minx[0], q_minx[1], q_minx[2], sm_min, sm_p10, sm_p90, sm_max, q_min, q_p10, q_p90, q_max]], columns= ["timestart", "pma", "etp", "q_obs", "smc_obs", "smc_var", "x1", "x2", "x3", "x4", "q3", "q4", "smc", "k", "fg1", "fg2","q4_min","q4_h1","q4_h2", "smc_min", "smc_p10", "smc_p90", "smc_max", "q_min", "q_p10", "q_p90", "q_max"])
            new_row_al = DataFrame([[timestart, x_al[0], x_al[1], x_al[2], x_al[3], q_al, sm_al, None]], columns= ["timestart", "x1", "x2", "x3", "x4", "q4", "smc","substeps"])

            ##################  CORRE PASO MODELO   #########################
            for j in range(self.replicates):
                p_alt = max(pma + np.random.normal(0,self.p_stddev * pma),0)
                pet_alt = max(etp + np.random.normal(0,self.pet_stddev),0)
                self.ens[j], npasos = self.advance_step(self.ens[j],p_alt,pet_alt, k)
                self.ens1[j], npasos = self.advance_step(self.ens1[j],p_alt,pet_alt, k)
                self.ens2[j], npasos = self.advance_step(self.ens2[j],p_alt,pet_alt, k)
            x_al, npasos = self.advance_step_and_pert(x_al,pma,etp, k)
            # $json_al .= ",\"n_pasos\":$npasos},"; #print $salida_al "$npasos\n";
            # $json_plus .= ",\"n_pasos\":$npasos,\"qobs\":" . ((defined $q) ? $q : "null") . ",\"smcobs\":" . ((defined $smc) ? $smc : "null") . "},";
            

            new_row_al.loc[[0],'substeps'] = npasos
            results = concat([results,new_row])
            results_al = concat([results,new_row_al])
            results_min = concat([results_min,new_row_min])
            results_h1 = concat([results_h1,new_row_h1])
            results_h2 = concat([results_h2,new_row_h2])
            if q_obs is not None:
                sim.append(Q_out_plus)
                obs.append(q_obs)

        results.set_index("timestart",inplace=True)
        results_al.set_index("timestart",inplace=True)
        results_min.set_index("timestart",inplace=True)
        results_h1.set_index("timestart",inplace=True)
        results_h2.set_index("timestart",inplace=True)
        # logging.debug(str(results))
        # results_no_na = results[["q_obs","q4"]].dropna()
        procedure_results = ProcedureFunctionResults(
            border_conditions = results[["pma","etp","q_obs","smc_obs","smc_var"]],
            initial_states = self.initial_states,
            states = results[["x1","x2","x3","x4"]],
            parameters = self.parameters,
            # "statistics": {
            #     "obs": results_no_na["q_obs"].tolist(),
            #     "sim": results_no_na["q4"].tolist(),
            #     "compute": True
            # }, 
            data = results.join([
                results_al.rename(columns={"x1":"x1_al","x2":"x2_al","x3":"x3_al","x4":"x4_al","q3":"q3_al","q4":"q4_al","smc":"smc_al"}), 
                results_min.rename(columns={"x1":"x1_min","x2":"x2_min","x3":"x3_min","x4":"x4_min","q4":"q4_min","smc":"smc_min"}), 
                results_h1.rename(columns={"x1":"x1_h1","x2":"x2_h1","x3":"x3_h1","x4":"x4_h1","q4":"q4_h1","smc":"smc_h1"}), 
                results_h2.rename(columns={"x1":"x1_h2","x2":"x2_h2","x3":"x3_h2","x4":"x4_h2","q4":"q4_h2","smc":"smc_h2"}), 
                DataFrame(KG_list).set_index("timestart")
            ])
        )
        return (
            [
                results[["q4","q_p10","q_p90"]].rename(columns={"q4":"valor", "q_p10": "inferior", "q_p90": "superior"}),
                results[["smc","smc_p10", "smc_p90"]].rename(columns={"smc":"valor","smc_p10": "inferior", "smc_p90": "superior"})
            ],
            procedure_results
        )
