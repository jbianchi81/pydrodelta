from .descriptors.string_descriptor import StringDescriptor
from .descriptors.float_descriptor import FloatDescriptor
from typing import Tuple

class ModelState:
    """Represents a procedure function state described by a name, a constraint range (min, max) and a default value"""

    name = StringDescriptor()
    """The state name"""

    min = FloatDescriptor()
    """The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash"""

    max = FloatDescriptor()
    """The maximum allowed value. A higher value is either physically impossible or would make the procedure crash"""

    default = FloatDescriptor()
    """The default value"""

    def __init__(
        self, 
        name : str, 
        constraints : Tuple[float,float],
        default = None
        ):
        """
        name : str

            The state name
        
        constraints : Tuple[float,float]

            tuple(min,max) where:
            - min: The minimum allowed value. A lower value is either physically impossible and/or would make the procedure crash
            - max: The maximum allowed value. A higher value is either physically impossible or would make the procedure crash

        default = None

            The default value
        """
        if not isinstance(constraints,(list,tuple)) or len(constraints) < 2:
            raise ValueError("constraints must be a 2-length list or tuple")
        self.name = name
        self.min = constraints[0]
        self.max = constraints[1]
        self.default = default
    
