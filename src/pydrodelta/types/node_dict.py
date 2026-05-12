from typing import TypedDict, List, Union, Any
from typing_extensions import NotRequired
from .hec_node_dict import HecNodeDict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
    tipo : NotRequired[str]
    timestart : NotRequired[datetime]
    timeend : NotRequired[datetime]
    forecast_timeend : NotRequired[datetime]
    plan : NotRequired[Any]
    time_offset : NotRequired[Union[timedelta, relativedelta]]
    topology : NotRequired[Any]
    hec_node : NotRequired[HecNodeDict]
    variables : NotRequired[List[Union[DerivedNodeVariableDict,ObservedNodeVariableDict]]]
    node_type : NotRequired[str]
    description : NotRequired[str]
    basin_pars : NotRequired[BasinParsDict]
    api_config : NotRequired[ApiConfigDict]
