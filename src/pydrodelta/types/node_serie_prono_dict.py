from typing import NotRequired, Required, Union, List
from .abstract_node_serie_dict import AbstractNodeSerieDict
from .plot_params_dict import PlotParamsDict
from a5client.util_types import Dateable

class NodeSeriePronoDict(AbstractNodeSerieDict, total=False):
    # required (overrides / extends base requirements)
    cal_id: Required[Union[int, None]]

    # optional
    qualifier: NotRequired[str]
    main_qualifier: NotRequired[str]

    adjust: NotRequired[bool]

    plot_params: NotRequired[PlotParamsDict]

    previous_runs_timestart: NotRequired[Dateable]
    forecast_timestart: NotRequired[Dateable]

    warmup: NotRequired[int]
    tail: NotRequired[int]

    sim_range: NotRequired[List[float]]