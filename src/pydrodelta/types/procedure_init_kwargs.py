from datetime import datetime
from typing import (
    Any,
    List,
    Mapping,
    Optional,
    Union,
    Literal,
    TYPE_CHECKING,
)

from typing_extensions import TypedDict
from .procedure_boundary_dict import ProcedureBoundaryDict
from a5client.util_types import TVPList, Intervaleable, Dateable
from pandas import DataFrame, Series
from ..model_parameter import ModelParameter

if TYPE_CHECKING:
    from ..plan import Plan

from ..util import IntervalDict

class ProcedureInitKwargs(TypedDict, total=False):
    """
    Keyword arguments accepted by Procedure.__init__().
    """
    
    # procedure identifier
    id: Union[int, str]

    plan: Optional["Plan"]

    initial_states: Union[list, dict]

    time_interval: Optional[
        Intervaleable
    ]

    time_offset: Optional[
        Union[float, IntervalDict]
    ]

    save_results: Optional[str]

    overwrite: bool

    overwrite_original: bool

    calibration: Optional[dict]

    adjust: bool

    adjust_method: Literal["lfit", "arima"]

    warmup_steps: Optional[int]

    tail_steps: Optional[int]

    error_band: Optional[bool]

    read_sim: bool

    sim_index: int

    save_dict: Optional[str]

    drop_warmup: bool

    boundaries: Optional[
        Union[
            str,
            List[ProcedureBoundaryDict],
            List[TVPList],
            List[List[float]],
            List[DataFrame],
            List[Series],
            DataFrame,
        ]
    ]

    outputs: Optional[
        Union[
            str,
            List[ProcedureBoundaryDict],
            List[TVPList],
            List[List[float]],
            List[DataFrame],
            List[Series],
            DataFrame,
        ]
    ]

    forecast_date: Optional[datetime]

    parameters_for_calibration: Optional[
        List[ModelParameter]
    ]

    timestart: Optional[Dateable]

    timeend: Optional[Dateable]