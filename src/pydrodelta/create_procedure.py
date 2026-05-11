from typing import TypeVar, Type, Dict, Any, Union
from pathlib import Path
import yaml
from pydrodelta.util import toMapping

from pydrodelta.procedure import Procedure
# from pydrodelta.procedures.hecras import HecRasProcedureFunction
# from pydrodelta.procedures.polynomial import PolynomialTransformationProcedureFunction
# from pydrodelta.procedures.muskingumchannel import MuskingumChannelProcedureFunction
# from pydrodelta.procedures.grp import GRPProcedureFunction
# from pydrodelta.procedures.linear_combination import LinearCombinationProcedureFunction
# from pydrodelta.procedures.expression import ExpressionProcedureFunction
# from pydrodelta.procedures.sacramento_simplified import SacramentoSimplifiedProcedureFunction
# from pydrodelta.procedures.sacramento_simplified_fixed_pars import SacramentoSimplifiedFixedParsProcedureFunction
# from pydrodelta.procedures.sac_enkf import SacEnkfProcedureFunction
# from pydrodelta.procedures.junction import JunctionProcedureFunction
# from pydrodelta.procedures.linear_channel import LinearChannelProcedureFunction
from pydrodelta.procedures.uh_linear_channel import UHLinearChannelProcedure
# from pydrodelta.procedures.gr4j_ import GR4JProcedureFunction as GR4J_ProcedureFunction
# from pydrodelta.procedures.gr4j import GR4JProcedureFunction
# from pydrodelta.procedures.linear_combination_2b import LinearCombination2BProcedureFunction
# from pydrodelta.procedures.linear_combination_3b import LinearCombination3BProcedureFunction
# from pydrodelta.procedures.linear_combination_4b import LinearCombination4BProcedureFunction
# from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedureFunction
# from pydrodelta.procedures.hosh4p1lnash import HOSH4P1LNashProcedureFunction
# from pydrodelta.procedures.hosh4p1luh import HOSH4P1LUHProcedureFunction
# from pydrodelta.procedures.difference import DifferenceProcedureFunction
# from pydrodelta.procedures.linear_net import LinearNetProcedureFunction
# from pydrodelta.procedures.linear_net_3 import LinearNet3ProcedureFunction
# from pydrodelta.procedures.exponential_fit import ExponentialFitProcedureFunction
# from pydrodelta.procedures.linear_fit import LinearFitProcedureFunction
# from pydrodelta.procedures.abstract import AbstractProcedureFunction
# from pydrodelta.procedures.lag_and_route import LagAndRouteProcedureFunction
# from pydrodelta.procedures.hidrosat import HIDROSATProcedureFunction
# from pydrodelta.procedures.analogy import AnalogyProcedureFunction
# from pydrodelta.procedures.persistence import PersistenceProcedureFunction
# from pydrodelta.procedures.lag_and_route_net import LagAndRouteNetProcedureFunction

PROCEDURES : Dict[str, Type[Procedure]]  = {
#     # "ProcedureFunction": ProcedureFunction,
#     "AbstractProcedureFunction": AbstractProcedureFunction,
#     "HecRas": HecRasProcedureFunction,
#     "HecRasProcedureFunction": HecRasProcedureFunction,
#     "PolynomialTransformationProcedureFunction": PolynomialTransformationProcedureFunction,
#     "Polynomial": PolynomialTransformationProcedureFunction,
#     "MuskingumChannel": MuskingumChannelProcedureFunction,
#     "MuskingumChannelProcedureFunction": MuskingumChannelProcedureFunction,
#     "GRP": GRPProcedureFunction,
#     "GRPProcedureFunction": GRPProcedureFunction,
#     "LinearCombination": LinearCombinationProcedureFunction,
#     "LinearCombination2B": LinearCombination2BProcedureFunction,
#     "LinearCombination3B": LinearCombination3BProcedureFunction,
#     "LinearCombination4B": LinearCombination4BProcedureFunction,
#     "Expression": ExpressionProcedureFunction,
#     "SacramentoSimplified": SacramentoSimplifiedProcedureFunction,
#     "SacramentoSimplifiedFixedPars": SacramentoSimplifiedFixedParsProcedureFunction,
#     "SacEnKF": SacEnkfProcedureFunction,
#     "Junction": JunctionProcedureFunction,
#     "LinearChannel": LinearChannelProcedureFunction,
     "UHLinearChannel": UHLinearChannelProcedure,
#     "GR4J": GR4JProcedureFunction,
#     "GR4J_": GR4J_ProcedureFunction,
#     "HOSH4P1L": HOSH4P1LProcedureFunction,
#     "HOSH4P1LNash": HOSH4P1LNashProcedureFunction,
#     "HOSH4P1LUH": HOSH4P1LUHProcedureFunction,
#     "Difference": DifferenceProcedureFunction,
#     "LinearNet": LinearNetProcedureFunction,
#     "LinearNet3": LinearNet3ProcedureFunction,
#     "ExponentialFit": ExponentialFitProcedureFunction,
#     "LinearFit": LinearFitProcedureFunction,
#     "LagAndRoute": LagAndRouteProcedureFunction,
#     "LagAndRouteNet": LagAndRouteNetProcedureFunction,
#     "HIDROSAT": HIDROSATProcedureFunction,
#     "Analogy": AnalogyProcedureFunction,
#     "Persistence": PersistenceProcedureFunction
}

def createProcedure(
        procedure_type : str,
        **kwargs: Any
    ) -> Procedure:
    cls = PROCEDURES[procedure_type]
    return cls(**kwargs)

def loadProcedure(
    file : Union[Path, str],
    **kwargs        
) -> Procedure:
    """Create procedure from yaml configuration file

        Args:
            file (str): path of yaml configuration file
            **kwargs: additional configuration parameters (dependant on the specific class)

        Returns:
            Plan: an object of this class according to the provided configuration
        """
    with open(file) as f:
        t_config = toMapping(yaml.safe_load(f))
    full_kwargs = {**t_config,**kwargs}
    full_kwargs["base_path"] = Path(file).resolve().parent
    if "type" not in full_kwargs:
        raise TypeError("Missing 'type'")
    procedure_type = full_kwargs["type"]
    del full_kwargs["type"]
    return createProcedure(procedure_type, **full_kwargs)



