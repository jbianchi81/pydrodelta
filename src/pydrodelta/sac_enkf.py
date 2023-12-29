import logging
from typing import Optional
from pydrodelta.series_data import SeriesData
from numpy import random
from pandas import DataFrame, Series, concat
# from math import sqrt

from pydrodelta.procedure_function import ProcedureFunctionResults
# from pydrodelta.qp import QPProcedureFunction
# from pydrodelta.util import interval2timedelta
import pydrodelta.sacramento_simplified as sac

kalman_def = {
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

class SacEnkfProcedureFunction(sac.SacramentoSimplifiedProcedureFunction):
    def __init__(self,params,procedure):
        """
        Instancia la clase. Lee la configuración del dict params, opcionalmente la valida contra un esquema y los guarda los parámetros y estados iniciales como propiedades de self.
        Guarda procedure en self._procedure (procedimiento al cual pertenece la función)
        """
        super(sac.SacramentoSimplifiedProcedureFunction,self).__init__(params,procedure)
        
        self.p_stddev, self.pet_stddev = self.extra_pars["stddev_forzantes"] if "stddev_forzantes" in self.extra_pars else kalman_def["stddev_forzantes"]
        self.x_stddev = self.extra_pars['stddev_estados'] if "stddev_estados" in self.extra_pars else kalman_def["x_stddev"]
        self.var_innov = self.extra_pars["var_innov"] if "var_innov" in self.extra_pars else kalman_def["var_innov"]
        self.trim_sm = self.extra_pars["trim_sm"] if "trim_sim" in self.extra_pars else kalman_def["trim_sim"]
        if self.var_innov[1] == "rule":
            if "rule" not in params:
                raise Exception("Missing parameter 'rule'")
            self.Rqobs = params["rule"]
        else:
            self.Rqobs = [[0,self.var_innov[0],0]]
        self.asim = self.extra_pars["asim"] if "asim" in self.extra_pars else kalman_def["asim"]
        self.update = [x.lower() if x is not None else None for x in self.extra_pars["update"]] if "update" in self.extra_parse else kalman_def["update"]
        self.xpert = self.extra_pars["xpert"] if "xpert" in self.extra_pars else kalman_def["xpert"]
        self.c1dia = self.c1
        self.c3dia = self.c3
        self.alfadia = self.alfa
        self.replicates = self.extra_pars["replicates"] if "replicates" in self.extra_pars else kalman_def["replicates"]
        self.setH()

        # states
        self.ens = list()
        self.ens1 = list()
        self.ens2 = list()
        self.mediassinpert = list()
        self.sm_obs = list()
        self.sm_sim = list()

        

    def xnoise(self,value,statename):
        pert = value * random.normal(loc=0,scale=self.x_stddev)
        pert = self.constraint(pert,statename)
        return pert

    def cero(self,value,max):
        if value <0:
            return 0
        elif value > max:
            return max
        else:
            return value

    def media(self,index):
        sum = 0
        sum1 = 0
        sum2 = 0
        for i in range(self.replicates):
            sum += self.ens[i][index]
            sum1 += self.ens1[i][index]
            sum2 += self.ens2[i][index]
        return (sum / self.replicates, sum1 / self.replicates, sum2 / self.replicates)

    def media1(self,index):
        sum = 0
        for i in range(self.replicates):
            sum += self.ens[i][index]
        return sum / self.replicates

    def covarianza(self,index_1,index_2):
        sum = 0
        for i in range(self.replicates):
            sum += (self.ens[i][index_1] - self.mediassinpert[index_1]) * (self.ens[i][index_2] - self.mediassinpert[index_2])
        return sum / self.replicates

    def q(self,value):
        for R in self.Rqobs:
            if value >= R[0]:
                return (R[1], R[2])

    def linfit(self,wsize,value):
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

    def advance_step_and_pert(self,x,pma,etp,pert=False):
        x = self.advance_step(x,pma,etp)
        # self.xsinpert = list(x)
        if self.xpert and pert:
            x[0] = self.xnoise(x[0],'x1')
            x[1] = self.xnoise(x[1],'x2')
            x[2] = self.xnoise(x[2],'x3')
            x[3] = self.xnoise(x[3],'x4')
        return (x[0],x[1],x[2],x[3])

    def setH(self):
        self.H = list()
        for i in range(2):
            if self.asim[i] is not None:
                H_row = list()
                for j in range(4):
                    if self.update[j] is not None:
                        H_row.append((self.rho - self.wp) / self.x1_0 if self.asim[i] == 'sm' and self.update[j] == 'x1' else self.alfa * self.area/1000/24/60/60 if self.asim[i] == 'q' and self.update[j] == 'x4' else 0)
                self.H.append(H_row)
        
    def setInitialEnsemble(self,init_states):
        for i in range(self.replicates):
            x1 =  max(0, min(init_states[0] + random.normal(0, self.x1_0 * self.x_stddev), self.x1_0))
            x2 =  max(0, min(init_states[1] + random.normal(0, self.x2_0 * self.x_stddev), self.x2_0))
            x3 = max(0, init_states[2] + random.normal(0, init_states[2] *  self.x_stddev))
            x4 = max(0, init_states[3] + random.normal(0, init_states[3] *  self.x_stddev))
            self.ens.append([x1,x2,x3,x4]) 
            # printf $ens "%.3f\t",$ens[$i][$j];
            self.ens1.append([x1,x2,x3,x4])
            self.ens2.append([x1,x2,x3,x4])
            #~ $json_rep[$i] = "{\"id\":$i,\"name\":\"replicate $i\",\"values\":[";
    





    def run(self,input: Optional[list[SeriesData]]=None) -> tuple[list[SeriesData], ProcedureFunctionResults]:
        """
        Ejecuta la función. Si input es None, ejecuta self._procedure.loadInput para generar el input. input debe ser una lista de objetos SeriesData
        Devuelve una lista de objetos SeriesData y opcionalmente un objeto ProcedureFunctionResults
        """
        init_states = [self.constraint(self.x[i],self.statenames[i]) for i in range(4)]
        self.setInitialEnsemble(init_states)
        x = list(init_states)
        x_al = list(init_states)
        denom_rk = (2,2,1)
        
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

        if len(input) < 2:
            raise Exception("Missing input series: at least pma and etp required")

        k = -1
        # iterate series using pma's index:
        for i, row in input[0].iterrows():
            k = k + 1
            pma = row["valor"]
            etp = input[1].loc[[i]].valor.item()
            q_obs = input[2].loc[[i]].valor.item() if len(input) > 2 else None
            smc_obs = input[3].loc[[i]].valor.item() if len(input) > 3 else None
            smc = (self.rho - self.wp) * x[0] / self.x1_0 + self.wp

            innov = dict()
            obs = []
            err = []
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
            if q_obs is not None and self.[1] is not None:
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
            my $sm_=(defined $smc) ? ($smc==-1) ? "" : $smc+$wp: "";
            if(! defined $p or ! defined $pet) {
                print STDERR "Falta valor de p o pet\n"; exit 1;
            }
            $json_al .= sprintf "{\"fecha_julian\":%.4f,\"fecha\":\"%s\",\"precip\":%.2f,\"pet\":%.2f,\"q_obs\":%s,\"smc_obs\":%s,\"x1\":%.4f,\"x2\":%.4f,\"x3\":%.4f,\"x4\":%.4f,\"caudal\":%.4f,\"smc\":%.4f", $jdate,@{$reg}[$paso]->{'fecha'},$p,$pet,($q_ ne "")?$q_:"null",($sm_ ne "")?$sm_:"null",$x_al[0],$x_al[1],$x_al[2],$x_al[3],$q_al,$sm_al;
            push @sm_obs, $sm_;
        #	$sm_=($sm_ ne "") ? &linfit($paso,$sm_) : "";
            #~ print $salida_Q "$jdate,$q_,";
            #~ print $salida_sm "$jdate,$sm_,";
            my $jd=$jdate-15018;
            #~ printf $salida "%.3f,%.3f,%.3f,%.3f,%.3f,", $jd,$p,$pet,$q,$smc;
            my @sm_f;
            my @q_f;
            my @q_minx;
            $j=0;
            $json_min .= "{";
            $json_h1 .= "{";
            $json_h2 .= "{";
            for($i=0;$i<=3;$i++)
            {
                my @media_f=&media($i);
                if($update[$i]=~/\D+/)
                {
                    $mediassinpert[$j]=$media_f[0];
                    $j++;
                }
                $json_min .= sprintf "\"x%d\":%.3f,",$i+1, $media_f[0];
                $json_h1 .= sprintf "\"x%d\":%.3f,",$i+1, $media_f[1];
                $json_h2 .= sprintf "\"x%d\":%.3f,",$i+1, $media_f[2];
                
                if($i==0)
                {
                    for(my $k=0;$k<=2;$k++)
                    {
                        $sm_f[$k]=$media_f[$k]*($rho-$wp)/$x1_0+$wp;			
                    }
                    $json_min .= sprintf "\"smc\":%.4f," , $sm_f[0];
                    $json_h1 .= sprintf "\"smc\":%.4f," , $sm_f[1];
                    $json_h2 .= sprintf "\"smc\":%.4f," , $sm_f[2];
        #			print $salida_sm "$sim,$sim1,$sim2,";
        #			printf $salida "%.3f,%.3f,",$q,$sim;
                }
                elsif($i==3)
                {
                    for(my $k=0;$k<=2;$k++)
                    {
                        $q_f[$k]=$media_f[$k]*$alfa*$area/1000/24/60/60;
                    }
                    $json_min .= sprintf "\"caudal\":%.4f," , $q_f[0];
                    $json_h1 .= sprintf "\"caudal\":%.4f," , $q_f[1];
                    $json_h2 .= sprintf "\"caudal\":%.4f," , $q_f[2];
                    @q_minx=($q_f[0], $q_f[1], $q_f[2]);
        #			print $salida_Q "$sim,$sim1,$sim2,";
        #			printf $salida "$smc,$sim";
                }
            }
            chop $json_min; $json_min .= "},";
            chop $json_h1; $json_h1 .= "},";
            chop $json_h2; $json_h2 .= "},";
        #	print $salida_Q "$q_al,";
        #	print $salida_sm "$sm_al,";

            
            




