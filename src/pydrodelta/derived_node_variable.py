from pydrodelta.node_variable import NodeVariable
from pydrodelta.derived_node_serie import DerivedNodeSerie
from pydrodelta.node_serie import NodeSerie
from pydrodelta.node_serie_prono import NodeSerieProno

class DerivedNodeVariable(NodeVariable):
    def __init__(self,params,node=None):
        super().__init__(params,node=node)
        self.series = []
        if "derived_from" in params:
            if self.series_output is None:
                raise Exception("missing series_output for derived node %s variable %s" % (str(self._node.id),str(self.id)))
            for serie in self.series_output:
                self.series.append(DerivedNodeSerie({"series_id":serie.series_id, "derived_from": params["derived_from"]},self._node._topology))
        elif "interpolated_from" in params:
            if self.series_output is None:
                raise Exception("missing series_output for derived node %s variable %s" % (str(self._node.id),str(self.id)))
            for serie in self.series_output:
                self.series.append(DerivedNodeSerie({"series_id":serie.series_id, "interpolated_from": params["interpolated_from"]},self._node._topology))
        if "series" in params:
            self.series.extend([NodeSerie(x) for x in params["series"]])
        if "series_prono" in params:
            self.series_prono = [NodeSerieProno(x) for x in params["series_prono"]]
        else:
            self.series_prono = None
    def derive(self):
        self.series[0].derive()
        self.data = self.series[0].data
        self.original_data = self.data.copy(deep=True)
        if hasattr(self.series[0],"max_obs_date"):
            self.max_obs_date = self.series[0].max_obs_date
