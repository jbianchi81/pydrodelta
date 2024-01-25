from numpy import random

class ModelParameter:
    def __init__(self, name:str=None, constraints:tuple=tuple()):
        if name is None:
            raise ValueError("Missing name")
        if len(constraints) < 4:
            raise ValueError("constraints must be a 4-length list or tuple")
        self.name = name
        self.min = float(constraints[0])
        self.range_min = float(constraints[1])
        self.range_max = float(constraints[2])
        self.max = float(constraints[3])
    
    def makeRandom(self,sigma=0.25,limit=True,range_min=None,range_max=None):
        """
        Generates random value using normal distribution centered between self.range_min and self.range_max
        The default sigma=0.25 (2-sigma) means that about 95% of the values will lie inside the range.
        If limit=True (default), values outside the self.min-self.max range will be limited
        """
        range_min = range_min if range_min is not None else self.range_min
        range_max = range_max if range_max is not None else self.range_max
        rand = range_min + random.normal(0.5,sigma) * (range_max - range_min)
        if limit:
            return self.min if rand < self.min else rand if rand < self.max else self.max
        else:
            return rand
