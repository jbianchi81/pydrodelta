from typing import TypedDict, List, Union
from .hec_node_dict import HecNodeDict
from datetime import datetime, timedelta
from .derived_node_variable_dict import DerivedNodeVariableDict
from .observed_node_variable_dict import ObservedNodeVariableDict
from .basin_pars_dict import BasinParsDict
from .api_config_dict import ApiConfigDict

class NodeDict(TypedDict):
    """
    Parameters:
    -----------
    id : int,
    
    name : str,
    
    time_interval : Union[dict,int],
    
    tipo : str="puntual",
    
    timestart : datetime = None,
    
    timeend : datetime = None,
    
    forecast_timeend : datetime = None,
    
    plan = None,
    
    time_offset : timedelta = None,
    
    topology = None,
    
    hec_node : dict = None,
    
    variables : List[Union[DerivedNodeVariable,ObservedNodeVariable]] = list(),
    
    node_type : str = "station",
    
    description : str = None,
    
    basin_pars : dict = None,
    
    api_config : dict = None

    """
    id : int
    name : str
    time_interval : Union[dict,int]
    tipo : str
    timestart : datetime
    timeend : datetime
    forecast_timeend : datetime
    plan : any
    time_offset : timedelta
    topology : any
    hec_node : HecNodeDict
    variables : List[Union[DerivedNodeVariableDict,ObservedNodeVariableDict]]
    node_type : str
    description : str
    basin_pars : BasinParsDict
    api_config : ApiConfigDict
