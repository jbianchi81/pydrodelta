from pydrodelta.util import interval2timedelta

class DerivedOrigin:
    def __init__(self,params,topology=None):
        self.node_id = params["node_id"]
        self.var_id = params["var_id"]
        self.x_offset = interval2timedelta(params["x_offset"]) if isinstance(params["x_offset"],dict) else params["x_offset"]
        self.y_offset = params["y_offset"]
        if topology is not None:
            from_nodes = [x for x in topology.nodes if x.id == self.node_id]
            if not len(from_nodes):
                raise Exception("origin node not found for derived variable, id: %i" % self.node_id)
            if self.var_id not in from_nodes[0].variables:
                raise Exception("origin variable not found for derived variable, node:id; %i, var_id: %i" % (self.node_id,self.var_id))
            self.origin = from_nodes[0].variables[self.var_id]
        else:
            self.origin = None
