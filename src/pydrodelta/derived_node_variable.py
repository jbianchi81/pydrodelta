from typing import List, Union, Optional, cast
from .node_variable import NodeVariable
from .derived_node_serie import DerivedNodeSerie
from .node_serie import NodeSerie
from .node_serie_prono import NodeSerieProno
from .types.derived_origin_dict import DerivedOriginDict
from .types.interpolated_origin_dict import InterpolatedOriginDict
from .types.typed_list import TypedList
from .descriptors.dict_descriptor import DictDescriptor

class DerivedNodeVariable(NodeVariable):
    """This class represents a variable at a node where it is not observed, but values are derived from observations of the same variable at a nearby node or from observations of another variable at the same  (or nearby) node"""
    
    derived_from = DictDescriptor()
    """Derivation configuration"""
    
    interpolated_from = DictDescriptor()
    """Interpolation configuration"""
        
    def _setDerivedSeries(self) -> None:
        if self.series_output is None:
            raise Exception("missing series_output for derived node %s variable %s" % (str(self._node.id) if self._node is not None else "unknown",str(self.id)))
        self._series = []
        for serie in self.series_output:
            self._series.append(
                DerivedNodeSerie(
                    series_id = serie.series_id, 
                    derived_from = self.derived_from,
                    topology = self._node._topology if self._node is not None else None,
                    base_path=self.base_path
                )
            )
    
    def _setInterpolatedSeries(self) -> None:
        if self.series_output is None:
            raise Exception("missing series_output for derived node %s variable %s" % (str(self._node.id) if self._node is not None else "unknown",str(self.id)))
        self._series = []
        for serie in self.series_output:
            self._series.append(
                DerivedNodeSerie(
                    series_id = serie.series_id, 
                    interpolated_from = self.interpolated_from,
                    topology = self._node._topology if self._node is not None else None,
                    base_path=self.base_path
                )
            )
    
    def __init__(
        self,
        derived_from : Optional[DerivedOriginDict] = None,
        interpolated_from : Optional[InterpolatedOriginDict] = None,
        derived : bool = True,
        **kwargs):
        """
        derived_from : DerivedOriginDict = None

            Derivation configuration

        interpolated_from : InterpolatedOriginDict = None

            Interpolation configuration

        series : List[Union[dict,NodeSerie]] = None
            
            Additional timeseries
            
        series_prono : List[Union[dict,NodeSerieProno]] = None

            Forecast timeseries

        **kwargs

            Keyword arguments. See NodeVariable (:class:`~pydrodelta.NodeVariable`)
        """
        super().__init__(**kwargs)
        series_ = [*self.series] if self.series is not None else None
        self.derived = True
        self.derived_from = derived_from
        self.interpolated_from = interpolated_from
        if derived_from is not None:
            self._setDerivedSeries()
        elif interpolated_from is not None:
            self._setInterpolatedSeries()
        else:
            self._series = []
        if series_ is not None:
            self._series.extend([x if isinstance(x, NodeSerie) else NodeSerie(**x, base_path=self.base_path) for x in series_])

    def derive(self) -> None:
        """Derive observations of .series[0] from associated node-variables"""
        if self.series is None or not len(self.series):
            raise Exception("series is not set")
        serie = self.series[0]
        if not isinstance(serie, DerivedNodeSerie):
            raise Exception("serie must be a DerivedNodeSerie")
        serie.derive()
        if serie.data is None:
            raise Exception("data not found")
        self.data = serie.data
        self.original_data = self.data.copy(deep=True)
        if hasattr(serie,"max_obs_date"):
            self.max_obs_date = serie.max_obs_date

    def __repr__(self):
        series_str = ", ".join(["Series(type: derived, id: %i)" % (s.series_id) for s in self.series]) if self.series is not None else "None"
        return "Variable(id: %i, name: %s, count: %i, series: [%s])" % (self.id, self.metadata["nombre"] if self.metadata is not None else None, len(self.data) if self.data is not None else 0, series_str)
