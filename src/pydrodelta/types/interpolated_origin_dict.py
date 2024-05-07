from typing import TypedDict, Union
from datetime import datetime

class InterpolatedOriginDict(TypedDict):
    """
    Parameters:
    -----------
    node_id_1 : int

    node_id_2 : int
    
    var_id_1 : int
    
    var_id_2 : int
    
    x_offset : Union[dict,datetime,float] = None
    
    y_offset : float = None
    
    interpolation_coefficient : float = 0.5
    """
    node_id_1 : int
    node_id_2 : int
    var_id_1 : int
    var_id_2 : int
    x_offset : Union[dict,datetime,float]
    y_offset : float
    interpolation_coefficient : float

