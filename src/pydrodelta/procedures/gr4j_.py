from pydrodelta.procedures.grp import GRPProcedureFunction
import logging
from numpy import tanh

class GR4JProcedureFunction(GRPProcedureFunction):
    def __init__(self,params,procedure):
        super().__init__(params,procedure) # super(PQProcedureFunction,self).__init__(params,procedure)
        # overrides UH1, SH1 from super
        self.UH1, self.SH1, self.UH2, self.SH2  = GR4JProcedureFunction.createUnitHydrograph(self.X3, self.alpha)

    @staticmethod
    def createUnitHydrograph(X3,alpha):
        t = 0
        UH1 = []
        SH1 = []
        UH2 = []
        SH2 = []
        while t <= int(2 * X3) + 1:
            logging.info("t: %i" % t)
            if t == 0:
                UH1.append(0)
                SH1.append(0)
                UH2.append(0)
                SH2.append(0)
            else:
                if t <= X3:
                    SH1.append((t / X3) ** alpha)
                    SH2.append(0.5 * (t / X3) ** alpha)
                elif t < 2 * X3:
                    SH1.append(1)
                    SH2.append(1 - 0.5 * (2 - t / X3) ** alpha)
                else:
                    SH1.append(1)
                    SH2.append(1)
                UH1.append(SH1[t] - SH1[t - 1])
                UH2.append(SH2[t] - SH2[t - 1])
            t = t + 1
        return UH1, SH1, UH2, SH2
    
    def advance_step(self,Sk: float,Rk: float,pma: float,etp: float,k: int,q_obs=None) -> tuple:
        Pn = pma - etp if pma >= etp else 0
        Ps = self.X0*(1-(Sk/self.X0)**2)*tanh(Pn/self.X0)/(1+Sk/self.X0*tanh(Pn/self.X0)) if Pn > 0 else 0
        Es = Sk*(2-Sk/self.X0)*tanh((etp-pma)/self.X0)/(1+(1-Sk/self.X0)*tanh((etp-pma)/self.X0)) if Pn == 0 else 0
        S1 = Sk + Ps - Es
        Perc = S1*(1-(1+(4/9*S1/self.X0)**4)**(-1/4))
        Sk_ = S1 - Perc
        self.Pr.append(Perc + Pn - Ps)
        Q9 = self.computeUnitHydrograph1(k)
        Q1 = self.computeUnitHydrograph2(k)
        F = self.X1 * (Rk / self.X2) ** (7/2)
        R1 = max(0, Rk + Q9 + F)
        Qr = R1 * (1 - (1 + (R1 / self.X2) ** 4) ** (-1/4))
        Qd = max(0, Q1 + F)
        Qk = (Qr + Qd) / 1000 / 24 / 60 / 60 / self.dt * self.area * self.ae
        Rk_ = R1 - Qr
        return Sk_, Rk_, Qk

    def computeUnitHydrograph1(self,k):
        j = 0
        Quh = 0
        while(j<min(int(self.X3)+1,k)):
            # logging.debug("j: %i, UH1[j]: %f" % (j,self.UH1[j]))
            # logging.debug("k: %i, Pr[k-j]: %f" % (k,self.Pr[k-j]))
            Quh = Quh + 0.9 * self.UH1[j]*self.Pr[k-j]
            j = j + 1
        return Quh 

    def computeUnitHydrograph2(self,k):
        j = 0
        Quh = 0
        while(j<min(int(2 * self.X3) + 1,k)):
            # logging.debug("j: %i, UH1[j]: %f" % (j,self.UH1[j]))
            # logging.debug("k: %i, Pr[k-j]: %f" % (k,self.Pr[k-j]))
            Quh = Quh + 0.1 * self.UH2[j]*self.Pr[k-j]
            j = j + 1
        return Quh 
