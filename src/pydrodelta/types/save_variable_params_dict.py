from typing import TypedDict, Union, Literal

class SaveVariableParamsDict(TypedDict):
    var_id : int
    nodes : list[int]
    output : str
    format : Literal["csv", "json"]
    pretty : bool
    pivot : bool