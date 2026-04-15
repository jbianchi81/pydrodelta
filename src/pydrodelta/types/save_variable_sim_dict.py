from typing import TypedDict, Union
from pathlib import Path

class SaveVariableSimDict(TypedDict):
    var_id : int
    output : Union[str,Path]
