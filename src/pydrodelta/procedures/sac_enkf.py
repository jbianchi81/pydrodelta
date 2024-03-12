import logging
from typing import Optional, List, Tuple, Union
from ..series_data import SeriesData
import numpy as np 
from pandas import DataFrame, Series, concat
from datetime import datetime

from ..procedure_function import ProcedureFunctionResults
import pydrodelta.procedures.sacramento_simplified as sac

from ..descriptors.list_descriptor import ListDescriptor

class SacEnkfProcedureFunction(sac.SacramentoSimplifiedProcedureFunction):
    """Simplified (10-parameter) Sacramento for precipitation - discharge transformation - ensemble with data assimilation. 
    
    Reference: https://www.researchgate.net/publication/348234919_Implementacion_de_un_procedimiento_de_pronostico_hidrologico_para_el_alerta_de_inundaciones_utilizando_datos_de_sensores_remotos"""

    _kalman_def = {
        "stddev_forzantes": [0.25,0.1],
        "x_stddev": 0.15,
        "var_innov": (0.03,"rule"),
        "trim_sm": (False,True),
        "asim": (None,'q'),
        "update": ('x1','x2','x3','x4'),
        "xpert": True,
        "sm_transform": (1,0),
        "replicates": 35,
        "windowsize": 1,
    }

    @property
    def p_stddev(self) -> float:
        """Standard deviation of the error of input precipitation"""
        return self.extra_pars["stddev_forzantes"][0] if "stddev_forzantes" in self.extra_pars else self._kalman_def["stddev_forzantes"]

    @property
    def pet_stddev(self) -> float:
        """Standard deviation of the error of input potential evapotranspiration"""
        return self.extra_pars["stddev_forzantes"][1] if "stddev_forzantes" in self.extra_pars else self._kalman_def["stddev_forzantes"]

    @property
    def x_stddev(self) -> float:
        """Standard deviation of the model states"""
        return self.extra_pars['stddev_estados'] if "stddev_estados" in self.extra_pars else self._kalman_def["x_stddev"]

    @property
    def var_innov(self) -> Tuple[Union[str,float],Union[str,float]]:
        """variance of the innovations (observation error): soil moisture (first element) and discharge (second element). If second element is 'rule', get variance of discharge from the rule defined in self.Rqobs"""
        return self.extra_pars["var_innov"] if "var_innov" in self.extra_pars else self._kalman_def["var_innov"]

    @property
    def trim_sm(self) -> Tuple[bool,bool]:
        """2-tuple of bool. Option to trim soil moisture observations at the low (wilting point, self.wf) and high (soil porosity, self.rho) values, respectively"""
        return self.extra_pars["trim_sm"] if "trim_sm" in self.extra_pars else self._kalman_def["trim_sm"]

    @property
    def Rqobs(self) -> List[Tuple[float,float,float]]:
        """Rule to determine observed discharge error variance as a function of the observed value. Ordered list of (threshold, bias, variance)"""
        if self.var_innov[1] == "rule":
            if "rule" not in self.extra_pars:
                raise Exception("Missing parameter 'rule'")
            return self.extra_pars["rule"]
        else:
            return [[0,self.var_innov[0],0]]

    @property
    def asim(self) -> Tuple[str,str]:
        """2-tuple of str or None. Option to assimilate soil moisture and discharge, respectively"""
        return self.extra_pars["asim"] if "asim" in self.extra_pars else self._kalman_def["asim"]

    @property
    def update(self) -> Tuple[str,str,str,str]:
        """4-tuple of str or None. Option to correct model states via data assimilation (x1, x2, x3, x4) """
        return [x.lower() if x is not None else None for x in self.extra_pars["update"]] if "update" in self.extra_pars else self._kalman_def["update"]

    @property
    def xpert(self) -> bool:
        """Option to add noise to model states at the beginning of each step"""
        return self.extra_pars["xpert"] if "xpert" in self.extra_pars else self._kalman_def["xpert"]

    @property
    def replicates(self) -> int:
        """Number of ensemble members"""
        return self.extra_pars["replicates"] if "replicates" in self.extra_pars else self._kalman_def["replicates"]

    ens = ListDescriptor()
    """Ensemble of model states (length = len(self.replicates) list of 4-tuples)"""

    ens1 = ListDescriptor()
    """Ensemble of model states without data assimilation in the last step (length = len(self.replicates) list of 4-tuples)"""
    
    ens2 = ListDescriptor()
    """Ensemble of model states without data assimilation in the last 2 steps (length = len(self.replicates) list of 4-tuples)"""
    
    mediassinpert = ListDescriptor()
    
    sm_obs = ListDescriptor()
    
    sm_sim = ListDescriptor()

    H = ListDescriptor()
    """The states transformation matrix"""

    _pivot_input : bool = True
    """Set to True if the run method requires a pivoted input"""

    def __init__(
        self,
        extra_pars : dict = dict(),
        **kwargs
        ):
        """
        extra_pars : dict = dict()
        
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

    def media(
        self,
        index : int
        ) -> Tuple[float,float,float]:
        """Get the ensemble mean of the model state variable of the selected index for each ensemble (self.ens, self.ens1, self.ens2)
        
        Parameters:
        -----------
        index : 0 <= int <= 3
        
        Returns:
        --------
        mean of ensemble 0 (self.ens) : float
        mean of ensemble 1 (self.ens1) : float
        mean of ensemble 2 (self.ens2) : float"""
        sum = 0
        sum1 = 0
        sum2 = 0
        for i in range(self.replicates):
            # logging.debug("sum: %s, self.ens[i][index]: %s" % (str(sum),str(self.ens[i][index])))
            sum += self.ens[i][index]
            sum1 += self.ens1[i][index]
            sum2 += self.ens2[i][index]
        return (sum / self.replicates, sum1 / self.replicates, sum2 / self.replicates)

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
        ) -> Tuple[float,float]:
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
        x : list,
        pma : float,
        etp : float
        ) -> Tuple[list,int]:
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
        x, npasos = self.advance_step(x,pma,etp)
        # self.xsinpert = list(x)
        if self.xpert:
            x = self.pertX(x)
        return [x[0],x[1],x[2],x[3]], npasos
    
    def pertX(
        self,
        x : list
        ) -> list:
        """Add noise to each of x [x1,x2,x3,x4]
        
        Parameters:
        -----------
        x : list
            Model states  [x1,x2,x3,x4]
        
        Returns:
        --------
        list :  [x1,x2,x3,x4]"""

        x[0] = self.xnoise(x[0],'x1')
        x[1] = self.xnoise(x[1],'x2')
        x[2] = self.xnoise(x[2],'x3')
        x[3] = self.xnoise(x[3],'x4')
        return [x[0],x[1],x[2],x[3]]

    def setH(self) -> None:
        """Set transformation matrix .H"""
        self.H = list()
        for i in range(2):
            if self.asim[i] is not None:
                H_row = list()
                for j in range(4):
                    if self.update[j] is not None:
                        H_row.append((self.rho - self.wp) / self.x1_0 if self.asim[i] == 'sm' and self.update[j] == 'x1' else self.alfa * self.area/1000/24/60/60 if self.asim[i] == 'q' and self.update[j] == 'x4' else 0)
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
            self.ens.append([x1,x2,x3,x4]) 
            # printf $ens "%.3f\t",$ens[$i][$j];
            self.ens1.append([x1,x2,x3,x4])
            self.ens2.append([x1,x2,x3,x4])
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
        innov : dict,
        qvar : float,
        smc_var : float
        ) -> Tuple[list,list]:
        """Generate observation error matrix R and adapt transformation matrix H into H_j according to available observations for assimilation

        Parameters:
        -----------
        innov : dict
            Which observed variables to assimilate. Valid keys: 'smc', 'q'. Values must be boolean

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
        R = list()
        H_j = list()
        k = 0
        l = 0
        for i in range(2):
            if self.asim[i] is not None:
                if innov[self.asim[i]]:
                    H_j.append(self.H[k])
                    row = list()
                    l = 0
                    for j in range(2):
                        if self.asim[j] is not None:
                            if innov[self.asim[j]]:
                                if k == l:
                                    if self.var_innov[i] == "rule":
                                        row.append(qvar)
                                    else:
                                        if self.var_innov[i] == "reg":
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
                    if self.update[l] is not None:
                        z += self.H[k][m] * self.ens[j][l]
                        m = m + 1
                err.append(obs[k] + np.random.normal(0, R[k][k] ** 0.5) - z)
                #~ print $salida_innov "$err[$k],";
            m = 0
            for k in range(len(self.ens[0])):
                z = 0
                if self.update[k] is not None:
                    for l in range(len(obs)):
                        z += KG_j[m][l] * err[l]
                    m = m + 1
                self.ens2[j][k] = self.ens1[j][k]
                self.ens1[j][k] = self.ens[j][k]
                self.ens[j][k] = self.constraint(self.ens[j][k] + z, self._statenames[k])
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
        timestart : datetime = None,
        x1 : float = None,
        x2 : float = None,
        x3 : float = None,
        x4 : float = None,
        q4 : float = None,
        smc : float = None
        ) -> DataFrame:
        """Generate single-row DataFrame from simulation states and outputs"""
        return DataFrame([[timestart, x1, x2, x3, x4, q4, smc]], columns= ["timestart", "x1", "x2", "x3", "x4", "q4", "smc"])

    def run(
        self,
        input : Optional[List[SeriesData]]=None
        ) -> Tuple[List[SeriesData], ProcedureFunctionResults]:
        init_states = [self.constraint(self.x[i],self._statenames[i]) for i in range(4)]
        self.setInitialEnsemble(init_states)
        x = list(init_states)
        x_al = list(init_states)
        denom_rk = (2,2,1)
        
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
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
            "q4_h2": Series(dtype="float")
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
            q_obs = input[2].loc[[timestart]].valor.item() if len(input) > 2 else None
            smc_obs = input[3].loc[[timestart]].valor.item() if len(input) > 3 else None
            smc_var = input[4].loc[[timestart]].valor.item() if len(input) > 4 else None
            smc = (self.rho - self.wp) * x[0] / self.x1_0 + self.wp

            innov = dict()
            obs = []
            if smc_obs is not None and self.asim[0] is not None:
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
            if ~np.isnan(q_obs) and self.asim[1] is not None:
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
            # $json_al .= sprintf "{\"fecha_julian\":%.4f,\"fecha\":\"%s\",\"precip\":%.2f,\"pet\":%.2f,\"q_obs\":%s,\"smc_obs\":%s,\"x1\":%.4f,\"x2\":%.4f,\"x3\":%.4f,\"x4\":%.4f,\"caudal\":%.4f,\"smc\":%.4f", $jdate,@{$reg}[$paso]->{'fecha'},$p,$pet,($q_ ne "")?$q_:"null",($sm_ ne "")?$sm_:"null",$x_al[0],$x_al[1],$x_al[2],$x_al[3],$q_al,$sm_al;
            self.sm_obs.append(sm_)
            #	$sm_=($sm_ ne "") ? &linfit($paso,$sm_) : "";
            #~ print $salida_Q "$jdate,$q_,";
            #~ print $salida_sm "$jdate,$sm_,";
            #~ printf $salida "%.3f,%.3f,%.3f,%.3f,%.3f,", $jd,$p,$pet,$q,$smc;
            # sm_f = list()
            # q_f = list()
            q_minx = list()
            j = 0
            new_row_min = self.newResultsRow(timestart)
            new_row_h1 = self.newResultsRow(timestart)
            new_row_h2 = self.newResultsRow(timestart)
            self.mediassinpert = list()
            for i in range(4):
                media_f = self.media(i)
                if self.update[i] is not None:
                    self.mediassinpert.append(media_f[0])
                    j = j + 1
                new_row_min.loc[[0],self._statenames[i]] = media_f[0] # $json_min .= sprintf "\"x%d\":%.3f,",$i+1, $media_f[0];
                new_row_h1.loc[[0],self._statenames[i]] = media_f[1] # $json_h1 .= sprintf "\"x%d\":%.3f,",$i+1, $media_f[1];
                new_row_h1.loc[[0],self._statenames[i]] = media_f[2] # $json_h2 .= sprintf "\"x%d\":%.3f,",$i+1, $media_f[2];
                
                if i == 0:
                    sm_f = list()
                    for k in range(3):
                        sm_f.append(media_f[k] * (self.rho - self.wp) / self.x1_0 + self.wp)
                    new_row_min.loc[[0],"smc"] = sm_f[0]
                    new_row_h1.loc[[0],"smc"] = sm_f[1] # $json_h1 .= sprintf "\"smc\":%.4f," , $sm_f[1];
                    new_row_h2.loc[[0],"smc"] = sm_f[2] # $json_h2 .= sprintf "\"smc\":%.4f," , $sm_f[2];
                elif i == 3:
                    q_f = list()
                    for k in range(3):
                        q_f.append(media_f[k] * self.alfa * self.area / 1000 / 24 / 60 / 60)
                    new_row_min.loc[[0],"q4"] = q_f[0] # $json_min .= sprintf "\"caudal\":%.4f," , $q_f[0];
                    new_row_h1.loc[[0],"q4"] = q_f[1] # $json_h1 .= sprintf "\"caudal\":%.4f," , $q_f[1];
                    new_row_h2.loc[[0],"q4"] = q_f[2] # $json_h2 .= sprintf "\"caudal\":%.4f," , $q_f[2];
                    q_minx = list(q_f)
            # chop $json_min; $json_min .= "},";
            # chop $json_h1; $json_h1 .= "},";
            # chop $json_h2; $json_h2 .= "},";
            C = self.getC()
            R, H_j = self.getR(innov,qvar,smc_var)
            if len(R) > 0:
                KG_j = self.getKG(H_j,C,R)
                err = self.asimila(obs,R,KG_j)
            else:
                KG_j = None
            
            KG_list.append({
                "timestart": timestart,
                "KG": KG_j.tolist() if KG_j is not None else None
            })
            
            ######CALCULA SMC Y Q SIMULADOS (PROMEDIO DEL ENSAMBLE)  ###############
            estados_prom = list()
            sim = list()
            errors = list()
            # my $kgstr = (@KG_j>0) ? encode_json(\@KG_j) : "\"null\"";
            # $json_plus .= sprintf "{\"fecha_julian\":%.4f,\"fecha\":\"%s\",\"kalman_gain\":$kgstr,\"estados\":[", $jdate, @{$reg}[$paso]->{'fecha'}; #print $salida_plus "$jdate\t";		
            for j in range(len(self.ens[0])):
                estados_prom.append(self.media1(j))
                # $json_plus .= sprintf "%.4f,", $estados_prom[$j];
            # chop $json_plus;
            # $json_plus .= "],";
            Q_out_plus = estados_prom[-1] * self.alfa * self.area / 1000 / 24 / 60 / 60
            Q3_plus = estados_prom[-2] * self.alfa * self.area / 1000 / 24 / 60 / 60
            sm_out_plus = estados_prom[0] * (self.rho - self.wp) / self.x1_0 + self.wp
            # $json_plus .= sprintf "\"caudal\":%.4f,\"smc\":%.4f", $Q_out_plus, $sm_out_plus; # print $salida_plus "\n";
            # $table_out .= sprintf "%s	%s	%.4f	%.4f	%.4f	%.4f	%.4f\n",@{$reg}[$paso]->{'fecha'}, (($q_ ne "")?$q_:"\\N"), $Q_out_plus, $q_al, @q_minx;   #### modif 2017-10-12 Qoutplus primero!!!
            ########## fg ##############
            if self.par_fg is not None:
                Qcurrent = q_ if q_ is not None else Q_out_plus
                (fg1, fg2) = self.computeFloodGuidance(estados_prom,Qcurrent)
            else:
                fg1 = None
                fg2 = None


            # write row
            new_row = DataFrame([[timestart, pma, etp, q_obs, smc_obs, smc_var, estados_prom[0], estados_prom[1], estados_prom[2], estados_prom[3], Q3_plus, Q_out_plus, sm_out_plus, k, fg1, fg2, q_minx[0], q_minx[1], q_minx[2]]], columns= ["timestart", "pma", "etp", "q_obs", "smc_obs", "smc_var", "x1", "x2", "x3", "x4", "q3", "q4", "smc", "k", "fg1", "fg2","q4_min","q4_h1","q4_h2"])
            new_row_al = DataFrame([[timestart, x_al[0], x_al[1], x_al[2], x_al[3], q_al, sm_al, None]], columns= ["timestart", "x1", "x2", "x3", "x4", "q4", "smc","substeps"])

            ##################  CORRE PASO MODELO   #########################
            for j in range(self.replicates):
                p_alt = max(pma + np.random.normal(0,self.p_stddev * pma),0)
                pet_alt = max(etp + np.random.normal(0,self.pet_stddev),0)
                self.ens[j], npasos = self.advance_step(list(self.ens[j]),p_alt,pet_alt)
                self.ens1[j], npasos = self.advance_step(list(self.ens1[j]),p_alt,pet_alt)
                self.ens2[j], npasos = self.advance_step(list(self.ens2[j]),p_alt,pet_alt)
            x_al, npasos = self.advance_step_and_pert(list(x_al),pma,etp)
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
                results[["q4"]].rename(columns={"q4":"valor"}),
                results[["smc"]].rename(columns={"smc":"valor"})
            ],
            procedure_results
        )
