from numpy import random
from typing import Tuple
from .descriptors.string_descriptor import StringDescriptor
from .descriptors.float_descriptor import FloatDescriptor

class ModelParameter:
    """Represents a procedure function parameter, described by a name and constraints. 

    Constraints:
    - min: The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash
    - range_min: The lower limit of the initial range of a random parameter set (for downhill simplex calibration)
    - range_max: The upper limit of the initial range of a random parameter set (for downhill simplex calibration)
    - max: The maximum allowed value. A higher value is either physically impossible or would make the procedure crash
    """
    name = StringDescriptor()
    """The parameter name"""

    min = FloatDescriptor()
    """The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash"""
    
    range_min = FloatDescriptor()
    """The lower limit of the initial range of a random parameter set (for downhill simplex calibration)"""
    
    range_max = FloatDescriptor()
    """The upper limit of the initial range of a random parameter set (for downhill simplex calibration)"""
    
    max = FloatDescriptor()
    """The maximum allowed value. A higher value is either physically impossible or would make the procedure crash"""
    
    def __init__(
        self,
        name : str, 
        constraints : Tuple[float,float,float,float]
        ):
        """
        name : str
        
            The name of the parameter
        
        constraints : Tuple[float,float,float,float]

            tuple(min, range_min, range_max, max), where:
            - min: The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash
            - range_min: The lower limit of the initial range of a random parameter set (for downhill simplex calibration)
            - range_max: The upper limit of the initial range of a random parameter set (for downhill simplex calibration)
            - max: The maximum allowed value. A higher value is either physically impossible or would make the procedure crash
        """
        if not isinstance(constraints,(list,tuple)) or len(constraints) < 4:
            raise ValueError("constraints must be a 4-length list or tuple")
        self.name = name
        self.min = constraints[0]
        self.range_min = constraints[1]
        self.range_max = constraints[2]
        self.max = constraints[3]
    
    def makeRandom(
        self,
        sigma : float = 0.25,
        limit : bool = True,
        range_min : float = None,
        range_max : float = None
        ) -> float:
        """
        Generates random value using normal distribution centered between self.range_min and self.range_max

        The default sigma=0.25 (2-sigma) means that about 95% of the values will lie inside the range.

        Parameters:
        -----------

        sigma : float = 0.25

            Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range

        limit : bool = True

            If limit=True (default), values lower than self.min will be set to self.lim and values higher that self.max will be set to self.max
        
        range_min : float = None

            Override self.range_min

        range_max : float = None

            Override self.range_max

        Returns:
        --------
        float
        """
        range_min = range_min if range_min is not None else self.range_min
        range_max = range_max if range_max is not None else self.range_max
        rand = range_min + random.normal(0.5,sigma) * (range_max - range_min)
        if limit:
            return self.min if rand < self.min else rand if rand < self.max else self.max
        else:
            return rand
