import logging

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
        self.errors = [self.sim[i] - self.obs[i] for i in range(0,len(self.sim))]
        self.n = len(self.errors)
        self.mse = sum([ e**2 for e in self.errors]) / len(self.errors)
        self.rmse = self.mse ** 0.5
        self.bias =  sum(self.errors) / self.n
        self.mean_obs = sum(self.obs) / self.n
        self.mean_sim = sum(self.sim) / self.n
        self.stdev_obs = sum([(x - self.mean_obs)**2 for x in self.obs]) / self.n
        self.stdev_sim = sum([(x - self.mean_sim)**2 for x in self.sim]) / self.n
        self.stdev_diff = self.stdev_sim - self.stdev_obs