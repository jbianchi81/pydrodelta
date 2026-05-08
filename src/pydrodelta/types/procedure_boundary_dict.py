from typing import TypedDict, Tuple
from typing_extensions import NotRequired
from pandas import DataFrame

class ProcedureBoundaryDict(TypedDict):
    name : str
    node_variable : Tuple[int,int]
    data : NotRequired[DataFrame]
