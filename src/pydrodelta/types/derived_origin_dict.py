from typing import Union, TypedDict
from datetime import datetime

class DerivedOriginDict(TypedDict):
    """
    Parameters:
    -----------
    node_id : int

    var_id : int
    
    x_offset : Union[dict,datetime,float] = None
    
    y_offset : float = None
    """
    node_id : int
    var_id : int
    x_offset : Union[dict,datetime,float] = None
    y_offset : float = None
