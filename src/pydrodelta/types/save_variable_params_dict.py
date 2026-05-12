from typing import TypedDict, Literal, List, Union
from typing_extensions import NotRequired
from pathlib import Path

class SaveVariableParamsDict(TypedDict):
    var_id : int
    nodes : NotRequired[List[int]]
    output : Union[str, Path]
    format : Literal["csv", "json"]
    pretty : NotRequired[bool]
    pivot : bool