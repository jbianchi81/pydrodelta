from typing import NotRequired, Union
from .abstract_node_serie_dict import AbstractNodeSerieDict
from .plot_params_dict import PlotParamsDict

class NodeSerieSimDict(AbstractNodeSerieDict, total=False):
    cal_id: NotRequired[Union[float, None]]

    qualifier: NotRequired[str]

    adjust: NotRequired[bool]

    plot_params: NotRequired[PlotParamsDict]

    upload: NotRequired[bool]