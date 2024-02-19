from typing import TypedDict, List
from .tvp import TVP

class SeriesDict(TypedDict):
    series_id : int
    series_table : str
    observaciones: List[TVP]
