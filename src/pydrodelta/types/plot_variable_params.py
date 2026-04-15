from typing import TypedDict, Optional
from datetime import datetime
from pathlib import Path

class PlotVariableParams(TypedDict):
    var_id : int
    output : Path
    timestart : Optional[datetime]
    timeend : Optional[datetime]
    extra_sim_columns : bool
    