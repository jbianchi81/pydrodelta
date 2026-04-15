from typing import TypedDict, Literal, List, Optional
from pathlib import Path

class SaveVariableParams(TypedDict):
    var_id : int
    output : Path
    format : Optional[Literal["csv", "json"]]
    pretty : bool
    pivot : bool