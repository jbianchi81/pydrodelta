from typing import TypedDict, Literal, List

class PointDict(TypedDict):
    type: Literal["Point"]
    coordinates: List[float]