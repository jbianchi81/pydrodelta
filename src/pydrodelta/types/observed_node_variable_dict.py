from .node_variable_dict import NodeVariableDict
from typing import Sequence, Union
# from .series_dict import SeriesDict
from .abstract_node_serie_dict import AbstractNodeSerieDict
from .series_prono_dict import SeriesPronoDict
from ..node_serie import NodeSerie
from ..node_serie_prono import NodeSerieProno

class ObservedNodeVariableDict(NodeVariableDict):
    """
        series : List[Union[SeriesDict,NodeSerie]]
        series_prono : List[Union[SeriesPronoDict,NodeSerieProno]]
    """
    series : Union[Sequence[AbstractNodeSerieDict],Sequence[NodeSerie]]
    series_prono : Union[Sequence[SeriesPronoDict],Sequence[NodeSerieProno]]
        