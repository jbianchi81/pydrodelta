from typing import TypedDict, Union, Optional
from typing_extensions import NotRequired
from a5client.util_types import Dateable
from pathlib import Path

class PlotVariableParamsDict(TypedDict):
    var_id : int
    output : Union[Path,str]
    timestart : NotRequired[Optional[Dateable]]
    timeend : NotRequired[Optional[Dateable]]
    extra_sim_columns : NotRequired[Optional[bool]]
    