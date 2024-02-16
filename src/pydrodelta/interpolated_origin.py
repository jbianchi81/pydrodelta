from pydrodelta.util import interval2timedelta
from typing import TypedDict, Union
from datetime import datetime

class InterpolatedOriginDict(TypedDict):
    node_id_1 : int
    node_id_2 : int
    var_id_1 : int
    var_id_2 : int
    x_offset : Union[dict,datetime,float] = None
    y_offset : float = None
    interpolation_coefficient : float = 0.5


class InterpolatedOrigin:
    def __init__(self,params,topology=None):
        self.node_id_1 = params["node_id_1"]
        self.node_id_2 = params["node_id_2"]
        self.var_id_1 = params["var_id_1"]
        self.var_id_2 = params["var_id_2"]
        self.x_offset = {"hours":0} if "x_offset" not in params else interval2timedelta(params["x_offset"]) if isinstance(params["x_offset"],dict) else params["x_offset"]
        self.y_offset = params["y_offset"] if "y_offset" in params else 0
        self.interpolation_coefficient = params["interpolation_coefficient"]
        if topology is not None:
            from_nodes = [x for x in topology.nodes if x.id == self.node_id_1]
            if not len(from_nodes):
                raise Exception("origin node not found for interpolated variable, id: %i" % self.interpolated_from.node_id_1)
            if self.var_id_1 not in from_nodes[0].variables:
                raise Exception("origin variable not found for interpolated variable, node:id; %i, var_id: %i" % (self.node_id_1,self.var_id_1))
            self.origin_1 = from_nodes[0].variables[self.var_id_1]
            from_nodes = [x for x in topology.nodes if x.id == self.node_id_2]
            if not len(from_nodes):
                raise Exception("origin node not found for interpolated node, id: %i" % self.node_id_2)
            if self.var_id_2 not in from_nodes[0].variables:
                raise Exception("origin variable not found for interpolated variable, node:id; %i, var_id: %i" % (self.node_id_2,self.var_id_2))
            self.origin_2 = from_nodes[0].variables[self.var_id_2]
        else:
            self.origin_1 = None
            self.origin_2 = None
