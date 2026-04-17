from typing import TypedDict, Optional, Literal

class AdjustFromDict(TypedDict):
    """
        truth: int
        sim: int
    """
    truth: int
    sim: int
    method : Optional[Literal["lfit","arima"]]