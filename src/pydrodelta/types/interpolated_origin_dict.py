from typing import TypedDict, Union, Optional
from datetime import datetime
from a5client.util_types import Intervaleable

class InterpolatedOriginDict(TypedDict):
    """
    Parameters:
    -----------
    node_id_1 : int

    node_id_2 : int
    
    var_id_1 : int
    
    var_id_2 : int
    
    x_offset : Optional[Itervaleable] = None
    
    y_offset : Optional[float] = None
    
    interpolation_coefficient : float = 0.5
    """
    node_id_1 : int
    node_id_2 : int
    var_id_1 : int
    var_id_2 : int
    x_offset : Optional[Intervaleable]
    y_offset : float
    interpolation_coefficient : float

