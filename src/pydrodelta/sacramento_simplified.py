import logging
from numpy import tanh
from typing import Optional
from pydrodelta.series_data import SeriesData
from pandas import DataFrame, Series, concat
from math import sqrt

from pydrodelta.procedure_function import ProcedureFunctionResults
from pydrodelta.qp import QPProcedureFunction

class par_fg():
    def __init__(self,parameters,area=None):
        self.CN2 = parameters["CN2"]
        self.hp1dia = parameters["hp1dia"]
        self.hp2dias = parameters["hp2dias"]
        self.Qbanca = parameters["Qbanca"]
        self.CN1 = 4.2 * self.CN2 / (10 - 0.058 * self.CN2)
        self.CN3 = 23 * self.CN2 / (10 + 0.13 * self.CN2)
        self.hp1dia = self.hp1dia * area/1000/1000 if area is not None else self.hp1dia
        self.hp2dias = self.hp2dias * area/1000/1000 if area is not None else self.hp2dias

class sm_transform():
    def __init__(self,parameters: list):
        self.slope = parameters[0]
        self.intercept = parameters[1]

class SacramentoSimplifiedProcedureFunction(QPProcedureFunction):
    def __init__(self,params,procedure):
        """
        Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
        Guarda procedure en self._procedure (procedimiento al cual pertenece la función)
        """
        super(QPProcedureFunction,self).__init__(params,procedure)

        self.fillnulls = self.parameters["fill_nulls"] if "fill_nulls" in self.parameters else False
        self.volume = 0
        self.x1_0 = self.parameters["x1_0"]
        self.x2_0 = self.parameters["x2_0"]
        self.m1 = self.parameters["m1"]
        self.c1 = self.parameters["c1"]
        self.c2 = self.parameters["c2"]
        self.c3 = self.parameters["c4"]
        self.mu = self.parameters["mu"]
        self.alfa = self.parameters["alfa"]
        self.m2 = self.parameters["m2"]
        self.m3 = self.parameters["m3"]
        self.denom_rk = (2,2,1)
        self.statenames = ['x1','x2','x3','x4']
        # self.npasos
        # self.max_npasos
        self.sm_obs = []
        self.sm_sim = []
        self.windowsize = self.parameters["windowsize"] if "windowsize" in self.parameters else None
        self.dt_sec = self.parameters["dt"].total_seconds() if "dt" in self.parameters else 24*60*60
        self.rho = self.parameters["rho"] if "rho" in self.parameters else 0.5
        self.area = self.parameters["area"]
        self.ae = self.parameters["ae"] if "ae" in self.parameters else 1
        self.wp = self.parameters["wp"] if "wp" in self.parameters else 0.03
        self.sm_transform = sm_transform(self.parameters["sm_transform"]) if "sm_transform" in self.parameters else sm_transform([1,0])
        self.x = [self.initial_states["x0"],self.initial_states["x1"],self.initial_states["x2"],self.initial_states["x3"]]
        # FLOOD GUIDANCE
        self.par_fg = par_fg(self.parameters["par_fg"],self.area) if "par_fg" in self.parameters else None
        # max substeps
        self.max_npasos = self.parameters["max_npasos"] if "max_npasos" in self.parameters else None
        self.no_check1 = self.parameters["no_check1"] if "no_check1" in self.parameters else False
        self.no_check2 = self.parameters["no_check2"] if "no_check2" in self.parameters else False
        self.rk2 = self.parameters["rk2"] if "rk2" in self.parameters else None
    
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
        X = []
        rk = 0
        while rk <= 3:
            sr = p * (x1 / self.x1_0)**self.m1
            pc = self.c3 * self.x2_0 * (1 + self.c2*(1 - x2 / self.x2_0)**self.m2) * (x1 / self.x1_0)
            et1 = pet * (x1 / self.x1_0)
            int = self.c1 * x1
            et2 = (pet - et1) * (x2 / self.x2_0)**self.m3
            gw = self.c3 * x2
            bf = (1 + self.mu)**(-1) * gw + int
            X[rk][0] = p - sr - pc - et1 - int
            X[rk][1] = pc - et2 - gw
            X[rk][2] = sr + bf
            if(rk<3):
                n1 = max(n1,self.check3(x1n,X[rk][0],1 / self.denom_rk[rk]))
            (n, fl) = self.check2(x2, self.x2_0, x1)
            n2 = max(n, n2)
            rk = 3 if fl == 1 else rk
            if(rk < 3):
                x1 = self.constraint(x1n + X[rk][0] / self.denom_rk[rk],'x1')
                x2 = self.constraint(x2n + X[rk][1] / self.denom_rk[rk],'x2')
            rk = rk + 1
        return (n1, n2)

    def advance_substep(self, x_n, p, pet, npasos):
        x_ = x_n            # @x_n: estados iniciales @x_: estados intermedios
        X = []                    # @X: derivadas
        rk = 0
        while rk <= 3:
            sr = p * (x_[0] / self.x1_0)**self.m1
            et1 = pet * (x_[0] / self.x1_0)
            int = self.c1 * x_[0]
            pc = self.c3 * self.x2_0 * (1 + self.c2*(1 - x_[1] / self.x2_0)**self.m2) * (x_[0] / self.x1_0)
            et2 = (pet - et1) * (x_[1] / self.x2_0)**self.m3
            gw = self.c3 * x_[1]
            bf = (1 + self.mu)**(-1) * gw + int
            X[rk][0] = p - sr - pc - et1 - int
            X[rk][1] = pc - et2 - gw
            X[rk][2] = sr + bf- x_[2] * self.alfa;
            X[rk][3] = x_[2] * self.alfa - x_[3] * self.alfa;
            rk = rk + 1
            sr = p * (x_[0] / self.x1_0) ** self.m1
            et1 = pet * (x_[0] / self.x1_0)
            int = self.c1 * x_[0]
            pc = self.c3 * self.x2_0 * (1 + self.c2 * ( 1 - x_[1] / self.x2_0) ** self.m2) * (x_[0] / self.x1_0)
            #~ $pc = ($pc/$_[6] > $x_[0] + ($p + $sr - $et1 - $int)/$_[6]) ? $x_[0] + ($p + $sr - $et1 - $int)/$_[6] : $pc;
            ### min($c3*$x2_0*(1+$c2*(1-$x_[1]/$x2_0)**$m2)*($x_[0]/$x1_0),$x_[0]+$p/$npasos-$sr/$npasos-$et1/$npasos-$int/$npasos);
            et2 = (pet - et1) * (x_[1] / self.x2_0) ** self.m3
            gw = self.c3 * x_[1]
            bf = (1 + self.mu) ** (-1) * gw + int
            X[rk][0] = p - sr - pc - et1 - int
            X[rk][1] = pc - et2 - gw
            X[rk][2] = sr + bf - x_[2] * self.alfa
            X[rk][3] = x_[2] * self.alfa - x_[3] * self.alfa
            # printf $rk_out "%s    %.2f    %d    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f\n",  $gl_date, $gl_mjd, $rk, $p, $pet, $x_[0], $x_[1], $x_[2], $x_[3], $sr, $et1, $int, $pc, $et2, $gw, $bf, $X[$rk][0],  $X[$rk][1],  $X[$rk][2],  $X[$rk][3];
            ### if rk2
            if self.rk2 is not None and rk == 0:
                for i in range(4):
                    x_[i] = self.constraint(x_n[i] + X[rk][i]/npasos,self.statenames[i])         
            else:
                out = []
                for k in range(4):
                    out[k] = self.constraint(x_n[k] + (X[0][k] + X[1][k]) / 2 / npasos,self.statenames[k])
                #~ @x = @out;
                return out[0], out[1], out[2], out[3]                        
                #~ last;
        else:    #### rk4
            if rk < 3:
                for i in range(4):
                    x_[i] = self.constraint(x_n[i] + X[rk][i] / self.denom_rk[rk]/npasos,self.statenames[i])
            else:
                out = []
                max = (self.x1_0,self.x2_0)
                for k in range(4):
                    out[k] = self.constraint(x_n[k] + (X[0][k] + 2 * X[1][k] + 2 * X[2][k] + X[3][k]) / 6 / npasos, self.statenames[k])
                return out[0], out[1], out[2], out[3]


    def advance_step(self,x,pma,etp):
        if not self.no_check1:
            npasos = max(1,int(pma/2))
        else:
            npasos = 1
        n1 = 1
        n2 = 1
        maxn = self.max_npasos if self.max_npasos is not None else 24
        if not self.no_check2:
            (n1, n2) = self.check(x[0],x[1],pma,etp)
        npasos = max(n2, max(npasos, min(24, n1)))
        npasos = npasos if self.max_npasos is None else min(self.max_npasos, npasos)
        l = 1
        while(l <= npasos):
            gl_mjd += 1/npasos
            x = self.advance_substep(x, pma, etp, npasos)
            # printf $super_out "%s    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f    %.2f\n", $gl_date, $gl_mjd, $_[4]/$npasos, $_[5]/$npasos, @x;
            l = l + 1

        return x[0], x[1], x[2], x[3]

    def run(self,input: Optional[list[SeriesData]]=None) -> tuple[list[SeriesData], ProcedureFunctionResults]:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        """
        if input is None:
            input = self._procedure.loadInput(inline=False,pivot=False)
        results = DataFrame({
            "timestart": Series(dtype='datetime64[ns]'),
            "pma": Series(dtype='float'),
            "etp": Series(dtype='float'),
            "q_obs": Series(dtype='float'),
            "smc_obs": Series(dtype='float'),
            "x0": Series(dtype='float'),
            "x1": Series(dtype='float'),
            "x2": Series(dtype='float'),
            "x3": Series(dtype='float'),
            "q3": Series(dtype='float'),
            "q4": Series(dtype='float'),
            "smc": Series(dtype='float'),
            "k": Series(dtype='int'),
            "fg1": Series(dtype='float'),
            "fg2": Series(dtype='float'),
            "substeps": Series(dtype='int')
        })
        results.set_index("timestart", inplace=True)
        # initialize states
        x = [self.constraint(self.x[i],self.statenames[i]) for i in range(4)]
        step = 0

        # series: pma*, etp*, q_obs, smc_obs [*: required]
        if len(input) < 2:
            raise Exception("Missing input series: at least pma and etp required")
        # instantiate lists for statistics computation
        sim = []
        obs = []
        sm_obs = []
        sm_sim = []
        k = -1
        # iterate series using pma's index:
        for i, row in input[0].iterrows():
            k = k + 1
            pma = row["valor"]
            etp = input[1].loc[[i]].valor.item()
            q_obs = input[2].loc[[i]].valor.item() if len(input) > 2 else None
            smc_obs = input[3].loc[[i]].valor.item() if len(input) > 3 else None
            smc = (self.rho - self.wp) * self.Sk / self.X0 + self.wp
            if pma is None:
                if self.fillnulls:
                    logging.warn("Missing pma value for date: %s. Filling up with 0" % i)
                    pma = 0
                else:
                    logging.warn("Missing pma value for date: %s. Unable to continue" % i)
                    break
            if etp is None:
                if self.fillnulls:
                    logging.warn("Missing etp value for date: %s. Filling up with 0" % i)
                    etp = 0
                else:
                    logging.warn("Missing etp value for date: %s. Unable to continue" % i)
                    break
            q3 = self.area * self.alfa * x[2] / 1000 / self.dt_sec * self.ae
            q4 = self.area * self.alfa * x[3] / 1000 / self.dt_sec * self.ae
            smcsim = (self.rho - self.wp) * x[0] / self.x1_0 + self.wp
            gl_date = i
            q_ = q_obs
            sm_ = min(max(smc,self.wp),self.rho) if smc is not None else None
            sm_obs.append(sm_)
            sm_sim.append(smcsim)
            # flood guidance
            if self.par_fg is not None:
                Qcurrent = q_ if q_ is not None else q4
                (fg1, fg2) = self.computeFloodGuidance(x,Qcurrent)
            else:
                fg1 = None
                fg2 = None

            # write row
            new_row = DataFrame([[i, pma, etp, q_obs, smc_obs, x[0], x[1], x[2], x[3], q3, q4, smcsim, k, fg1, fg2, None]], columns= ["timestart", "pma", "etp", "q_obs", "smc_obs", "x0", "x1", "x2", "x3", "q3", "q4", "smc", "k", "fg1", "fg2","substeps"])

            #advance step
            (x, npasos) = self.advance_step(x,pma,etp)
            new_row.loc[[0],'substeps'] = npasos
            results = concat([results,new_row])
            if q_obs is not None:
                sim.append(q4)
                obs.append(q_obs)

        results = results.set_index("timestart")
        # logging.debug(str(results))
        procedure_results = ProcedureFunctionResults({
            "border_conditions": results[["pma","etp","q_obs","smc_obs"]],
            "init_states": {
                "Sk": self.Sk_init,
                "Rk": self.Rk_init
            },
            "states": results[["Sk","Rk"]],
            "parameters": {
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
            "statistics": {
                "obs": obs,
                "sim": sim,
                "compute": True
            }
        })
        return [results[["q"]].rename(columns={"q":"valor"}),results[["smc"]].rename(columns={"smc":"valor"})], procedure_results 
    
    def advance_step(self,Sk: float,Rk: float,pma: float,etp: float,k: int,q_obs: Optional[float]=None) -> tuple[float,float,float]:
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
            Qt = q_obs * 1000 * 24 * 60 * 60 * self.dt / self.area / self.ae
            R1 = ((Qt ** 2 + 4 * self.X1 * Qt) ** 0.5 + Qt) / 2
        Qr = R1 ** 2 / (R1 + self.X1)
        Qk = Qr / 1000 / 24 / 60 / 60 / self.dt * self.area * self.ae
        Rk_ = R1 - Qr
        return Sk_, Rk_, Qk

    def computeUnitHydrograph(self,k):
        j = 0
        Quh = 0
        while(j<min(int(self.X3)+1,k)):
            # logging.debug("j: %i, UH1[j]: %f" % (j,self.UH1[j]))
            # logging.debug("k: %i, Pr[k-j]: %f" % (k,self.Pr[k-j]))
            Quh = Quh + self.UH1[j]*self.Pr[k-j]
            j = j + 1
        return Quh 
