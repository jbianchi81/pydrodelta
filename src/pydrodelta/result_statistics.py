import logging
from pandas import DataFrame
import math

class ResultStatistics:
    def __init__(self,params:dict={}):
        self.obs = params["obs"] if "obs" in params else [] 
        self.sim = params["sim"] if "sim" in params else []
        if params["compute"]:
            self.compute()

    def compute(self):
        if not len(self.sim):
            logging.warn("No values found for statistics computation, skipping")
            return
        if len(self.obs) != len(self.sim):
            raise Exception("Length of obs and sim lists must be equal")
        df = DataFrame({"obs":self.obs,"sim":self.sim})
        df = df.dropna()
        self.errors = [self.sim[i] - self.obs[i] for i in range(0,len(self.sim))]
        df["errors"] = df["sim"] - df["obs"]
        self.errors = [v for v in df["errors"]]
        self.n = len(df["errors"])
        self.mse = sum([ e**2 for e in self.errors]) / len(self.errors)
        self.rmse = self.mse ** 0.5
        self.bias =  sum(self.errors) / self.n
        self.mean_obs = sum(df["obs"]) / self.n
        self.mean_sim = sum(df["sim"]) / self.n
        self.stdev_obs = sum([(x - self.mean_obs)**2 for x in df["obs"]]) / self.n
        self.stdev_sim = sum([(x - self.mean_sim)**2 for x in df["sim"]]) / self.n
        self.stdev_diff = self.stdev_sim - self.stdev_obs
        self.obs = [v for v in df["obs"]]
        self.sim = [v for v in df["sim"]]
        self.nse = 1 - self.mse / self.stdev_obs
    def toDict(self):
        dict = self.__dict__
        # dict["obs"] = [v  if not math.isnan(v) else None for v in dict["obs"]]
        # dict["sim"] = [v  if not math.isnan(v) else None for v in dict["sim"]]
        return dict