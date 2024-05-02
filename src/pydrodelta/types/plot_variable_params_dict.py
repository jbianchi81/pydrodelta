from typing import TypedDict, Union
from datetime import datetime

class PlotVariableParamsDict(TypedDict):
    var_id : int
    timestart : Union[datetime,str,dict]
    timeend : Union[datetime,str,dict]
    extra_sim_columns : bool