# from pydrodelta.node_variable import NodeVariable 

class ProcedureBoundary():
    """
    A variable at a node which is used as a procedure boundary condition
    """
    def __init__(self,params:dict,plan=None,optional=False,warmup_only=False,compute_statistics=True):
        self.optional = optional
        print("params: %s" % str(params))
        self.node_id = int(params["node_variable"][0])
        self.var_id = int(params["node_variable"][1])
        self.name = params["name"] # if name is not None else "%i_%i" % (self.node_id, self.var_id) # str(params[2]) if len(params) > 2 else "%i_%i" % (self.node_id, self.var_id)
        if plan is not None:
            self.setNodeVariable(plan)
            self._plan = plan
        else:
            self._variable = None
            self._node = None
            self._plan = None
        self.warmup_only = warmup_only
        self.compute_statistics = compute_statistics
    def __dict__(self):
        return {
            "optional": self.optional,
            "node_id": self.node_id,
            "var_id": self.var_id,
            "name": self.name,
            "warmup_only": self.warmup_only,
            "compute_statistics": self.compute_statistics
        }
    def setNodeVariable(self,plan):
        for t_node in plan.topology.nodes:
            if t_node.id == self.node_id:
                self._node = t_node
                if self.var_id in t_node.variables:
                    self._variable = t_node.variables[self.var_id]
                    return
        raise Exception("ProcedureBoundary.setNodeVariable error: node with id: %s , var %i not found in topology" % (str(self.node_id), self.var_id))
    def assertNoNaN(self,warmup_only=False):
        if self._variable is None:
            raise AssertionError("procedure boundary variable is None")
        if self._variable.data is None:
            raise AssertionError("procedure boundary data is None")
        if warmup_only:
            na_count = self._variable.data[self._variable.data.index <= self._plan.forecast_date]["valor"].isna().sum()
        else:
            na_count = self._variable.data["valor"].isna().sum()
        if na_count > 0:
            first_na_datetime = self._variable.data[self._variable.data["valor"].isna()].iloc[0].name.isoformat()
            raise AssertionError("procedure boundary variable data has NaN values starting at position %s" % first_na_datetime)
        return
