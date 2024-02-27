from typing import TypedDict, Tuple

class ProcedureBoundaryDict(TypedDict):
    name : str
    node_variable : Tuple[int,int]