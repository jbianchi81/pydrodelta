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

    _required_extra_pars : list = ["area"]
    """When inheriting this class, override this property according to the procedure requirements. Method self.setBasinMetadata iterates this list to check for missing extra parameters (e.g. basin parameters)"""

    def __init__(
        self,
        extra_pars : dict = dict(),
        **kwargs):
        super().__init__(extra_pars = extra_pars, **kwargs)
        getSchemaAndValidate(dict(kwargs, extra_pars = extra_pars),"PQProcedureFunction")
        if self.fill_nulls:
            logging.debug("PQProcedure - fillnulls: setting pma boundary to optional")
            self.boundaries.getById("pma").optional = True
        self.setBasinMetadata()

    def setBasinMetadata(self) -> None:
        # if self.boundaries.getById("pma").node.node_type == "basin":
        for key in self._required_extra_pars:
            if key not in self.extra_pars or self.extra_pars[key] is None:
                if self.boundaries.getById("pma").node is None:
                    raise ValueError("Missing key '%s' from extra_pars" % key)
                if self.boundaries.getById("pma").node.basin_pars is None:
                    raise Exception("Missing key '%s' in self.extra_pars with no self.boundariesgetById('pma').node.basin_pars from which to read defaults" % key)
                if key not in self.boundaries.getById("pma").node.basin_pars or self.boundaries.getById("pma").node.basin_pars[key] is None:
                    raise Exception("key '%s' missing from either self.extra_pars or self.boundaries.getById('pma').node.basin_pars" % key)
                logging.debug("Basin parameter '%s' missing from procedure function input. Filling up with self.boundaries.getById('pma').node.basin_pars" % key)
                self.extra_pars[key] = self.boundaries.getById("pma").node.basin_pars[key]
