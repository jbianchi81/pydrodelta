from typing import TypedDict

class ProcedureBoundaryDict(TypedDict):
    name : str
    node_variable : tuple[int,int]