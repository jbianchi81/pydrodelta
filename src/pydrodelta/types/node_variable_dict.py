from typing import TypedDict, Union, List
from ..node_serie import NodeSerie
from .series_dict import SeriesDict
from datetime import datetime, timedelta
from .adjust_from_dict import AdjustFromDict
from .linear_combination_dict import LinearCombinationDict

class NodeVariableDict(TypedDict):
    """
        id : int,
        node = None,
        fill_value : float = None,
        series_output : List[Union[NodeSerie,SeriesDict]] = None,
        output_series_id : int = None,
        series_sim : List[Union[NodeSerie,SeriesDict]] = None,
        time_support : Union[datetime,dict,int,str] = None,
        adjust_from : AdjustFromDict = None,
        linear_combination : LinearCombinationDict = None,
        interpolation_limit : int = None,
        extrapolate : bool = None,
        time_interval : Union[timedelta,dict,float] = None,
        name : str = None,
        timestart : datetime = None,
        timeend : datetime = None,
        time_offset : timedelta = None,
        forecast_timeend : datetime = None
    """
    id : int
    node : any
    fill_value : float
    series_output : List[Union[NodeSerie,SeriesDict]]
    output_series_id : int
    series_sim : List[Union[NodeSerie,SeriesDict]]
    time_support : Union[datetime,dict,int,str]
    adjust_from : AdjustFromDict
    linear_combination : LinearCombinationDict
    interpolation_limit : int
    extrapolate : bool
    time_interval : Union[timedelta,dict,float]
    name : str
    timestart : datetime
    timeend : datetime
    time_offset : timedelta
    forecast_timeend : datetime