from typing import TypedDict, Optional
from .point_dict import PointDict

class StationParsDict(TypedDict):
    id: int
    geom: Optional[PointDict]
    nombre: Optional[str]
    tabla: Optional[str]