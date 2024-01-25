import logging
from pandas import DataFrame
import math

class ResultStatistics:
    def __init__(self,params:dict={}):
        self.obs = list(params["obs"]) if "obs" in params and params["obs"] is not None else list() 
        self.sim = list(params["sim"]) if "sim" in params and params["sim"] is not None else list()
        self.metadata = dict(params["metadata"]) if "metadata" in params else None
        self.error = None
        self.n = None
        self.mse = None
        self.rmse = None
        self.bias =  None
        self.mean_obs = None
        self.mean_sim = None
        self.stdev_obs = None
        self.stdev_sim = None
        self.stdev_diff = None
        self.nse = None
        self.var_obs = None
        self.var_sim = None
        self.cov = None
        self.r = None
        if "compute" in params and params["compute"]:
            self.compute()

    def compute(self):
        if not len(self.sim):
            logging.warn("No values found for statistics computation, skipping")
            return
        if len(self.obs) != len(self.sim):
            logging.warn("Length of obs and sim lists must be equal. No computation performed")
            return
        df = DataFrame({"obs":self.obs,"sim":self.sim})
        df = df.dropna()
        self.errors = [self.sim[i] - self.obs[i] for i in range(0,len(self.sim))]
        df["errors"] = df["sim"] - df["obs"]
        self.errors = [v for v in df["errors"]]
        self.n = len(df["errors"])
        if len(self.errors) == 0:
            logging.warn("No obs/sim pairs found for error calculation")
            return
        self.mse = sum([ e**2 for e in self.errors]) / len(self.errors)
        self.rmse = self.mse ** 0.5
        self.bias =  sum(self.errors) / self.n
        self.mean_obs = sum(df["obs"]) / self.n
        self.mean_sim = sum(df["sim"]) / self.n
        self.stdev_obs = sum([(x - self.mean_obs)**2 for x in df["obs"]]) / self.n
        self.stdev_sim = sum([(x - self.mean_sim)**2 for x in df["sim"]]) / self.n
        self.var_obs = self.stdev_obs ** 0.5
        self.var_sim = self.stdev_sim ** 0.5
        self.stdev_diff = self.stdev_sim - self.stdev_obs
        self.obs = [v for v in df["obs"]]
        self.sim = [v for v in df["sim"]]
        self.nse = 1 - self.mse / self.stdev_obs if self.stdev_obs != 0 else None
        self.cov = sum([ (self.obs[i] - self.mean_obs) * (self.sim[i] - self.mean_sim) for i in range(len(self.obs))]) / self.n
        self.r = self.cov / self.var_obs / self.var_sim if self.var_obs != 0 and self.var_sim != 0 else None
    def toDict(self):
        dict = self.__dict__
        # dict["obs"] = [v  if not math.isnan(v) else None for v in dict["obs"]]
        # dict["sim"] = [v  if not math.isnan(v) else None for v in dict["sim"]]
        return dict