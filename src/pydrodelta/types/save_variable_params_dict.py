from typing import TypedDict, Literal, List

class SaveVariableParamsDict(TypedDict):
    var_id : int
    nodes : List[int]
    output : str
    format : Literal["csv", "json"]
    pretty : bool
    pivot : bool