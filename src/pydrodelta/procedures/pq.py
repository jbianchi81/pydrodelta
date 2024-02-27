from ..procedure_function import ProcedureFunction
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary

import logging

class PQProcedureFunction(ProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "pma"}),
        FunctionBoundary({"name": "etp"}),
        FunctionBoundary({"name": "q_obs", "optional": True}),
        FunctionBoundary({"name": "smc_obs", "optional": True})
    ]
    """Procedure function boundary definition"""

    _outputs = [
        FunctionBoundary({"name": "q_sim"}),
        FunctionBoundary({"name": "smc_sim"})
    ]
    """Procedure function output definition"""

    @property
    def fill_nulls(self) -> bool:
        """If missing PMAD values, fill up with zeros"""
        return bool(self.extra_pars["fill_nulls"]) if "fill_nulls" in self.extra_pars else False


    @property
    def area(self) -> float:
        """basin area in square meters"""
        return float(self.extra_pars["area"])
    
    @property
    def ae(self) -> float:
        """effective area (0-1)"""
        return float(self.extra_pars["ae"]) if "ae" in self.extra_pars else 1
    
    @property
    def rho(self) -> float:
        """soil porosity (0-1)"""
        return float(self.extra_pars["rho"]) if "rho" in self.extra_pars else 0.5
    
    @property
    def wp(self) -> float:
        """wilting point of soil (0-1)"""
        return float(self.extra_pars["wp"]) if "wp" in self.extra_pars else 0.03

    def __init__(
        self,
        extra_pars : dict = dict(),
        **kwargs):
        super().__init__(extra_pars = extra_pars, **kwargs)
        getSchemaAndValidate(dict(kwargs, extra_pars = extra_pars),"PQProcedureFunction")
        if self.fill_nulls:
            logging.debug("PQProcedure - fillnulls: setting pma boundary to optional")
            self.boundaries[0].optional = True
