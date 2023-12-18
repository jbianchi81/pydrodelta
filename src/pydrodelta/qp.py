from pydrodelta.procedure_function import ProcedureFunction
from pydrodelta.validation import getSchema, validate
from pydrodelta.function_boundary import FunctionBoundary

schemas, resolver = getSchema("PQProcedureFunction","data/schemas/json")
schema = schemas["PQProcedureFunction"]

class QPProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "pma"}),
        FunctionBoundary({"name": "etp"}),
        FunctionBoundary({"name": "q_obs", "optional": True}),
        FunctionBoundary({"name": "smc_obs", "optional": True})
    ]
    _outputs = [
        FunctionBoundary({"name": "q_sim"}),
        FunctionBoundary({"name": "smc_sim"})
    ]
    def __init__(self,params,procedure):
        super(ProcedureFunction,self).__init__(params,procedure)
        validate(params,schema,resolver)
        # self.parameters = params["parameters"] if "parameters" in params else {}
        # self.init_states = params["init_states"] if "init_states" in params else {}
