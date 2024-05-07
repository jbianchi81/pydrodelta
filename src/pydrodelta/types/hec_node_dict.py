from typing import TypedDict

class HecNodeDict(TypedDict):
    """
        River  : str
        Reach : str
        River_Stat : int
        Interval : str
        CondBorde: str
    """
    River  : str
    Reach : str
    River_Stat : int
    Interval : str
    CondBorde: str