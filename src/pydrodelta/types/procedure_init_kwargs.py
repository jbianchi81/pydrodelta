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
from numpy import floating
from numpy.typing import NDArray

if TYPE_CHECKING:
    from ..plan import Plan

from ..util import IntervalDict
from .any_calibration_dict import AnyCalibrationDict

class ProcedureInitKwargs(TypedDict, total=False):
    """
    Keyword arguments accepted by Procedure.__init__().
    """
    
    # procedure identifier
    id: Union[int, str]

    plan: Optional["Plan"]

    time_interval: Optional[
        Intervaleable
    ]

    time_offset: Optional[
        Intervaleable
    ]

    save_results: Optional[str]

    overwrite: bool

    overwrite_original: bool

    calibration: Optional[AnyCalibrationDict]

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
            NDArray[floating]
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
            NDArray[floating]
        ]
    ]

    forecast_date: Optional[Dateable]

    parameters_for_calibration: Optional[
        List[ModelParameter]
    ]

    timestart: Optional[Dateable]

    timeend: Optional[Dateable]

    bias_correction: Optional[bool]
