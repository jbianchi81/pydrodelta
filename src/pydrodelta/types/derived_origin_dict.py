from typing import TypedDict, Optional
from a5client.util_types import Intervaleable

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
    x_offset : Optional[Intervaleable]
    y_offset : Optional[float]
