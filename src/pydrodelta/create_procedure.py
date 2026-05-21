from typing import TypeVar, Type, Dict, Any, Union
from pathlib import Path
import yaml
from pydrodelta.util import toMapping

from pydrodelta.procedure import Procedure
from pydrodelta.procedures.hecras import HecRasProcedure
from pydrodelta.procedures.polynomial import PolynomialTransformationProcedure
from pydrodelta.procedures.muskingumchannel import MuskingumChannelProcedure
from pydrodelta.procedures.grp import GRPProcedure
from pydrodelta.procedures.linear_combination import LinearCombinationProcedure
from pydrodelta.procedures.expression import ExpressionProcedure
from pydrodelta.procedures.sacramento_simplified import SacramentoSimplifiedProcedure
from pydrodelta.procedures.sacramento_simplified_fixed_pars import SacramentoSimplifiedFixedParsProcedure
from pydrodelta.procedures.sac_enkf import SacEnkfProcedure
from pydrodelta.procedures.junction import JunctionProcedure
from pydrodelta.procedures.linear_channel import LinearChannelProcedure
from pydrodelta.procedures.uh_linear_channel import UHLinearChannelProcedure
from pydrodelta.procedures.gr4j_ import GR4JProcedure as GR4J_Procedure
from pydrodelta.procedures.gr4j import GR4JProcedure
from pydrodelta.procedures.linear_combination_2b import LinearCombination2BProcedure
from pydrodelta.procedures.linear_combination_3b import LinearCombination3BProcedure
from pydrodelta.procedures.linear_combination_4b import LinearCombination4BProcedure
from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedure
from pydrodelta.procedures.hosh4p1lnash import HOSH4P1LNashProcedure
from pydrodelta.procedures.hosh4p1luh import HOSH4P1LUHProcedure
from pydrodelta.procedures.difference import DifferenceProcedure
from pydrodelta.procedures.linear_net import LinearNetProcedure
from pydrodelta.procedures.linear_net_3 import LinearNet3Procedure
from pydrodelta.procedures.exponential_fit import ExponentialFitProcedure
from pydrodelta.procedures.linear_fit import LinearFitProcedure
from pydrodelta.procedures.abstract import AbstractProcedure
from pydrodelta.procedures.lag_and_route import LagAndRouteProcedure
from pydrodelta.procedures.hidrosat import HIDROSATProcedure
from pydrodelta.procedures.analogy import AnalogyProcedure
from pydrodelta.procedures.persistence import PersistenceProcedure
from pydrodelta.procedures.lag_and_route_net import LagAndRouteNetProcedure

PROCEDURES : Dict[str, Type[Procedure]]  = {
    "AbstractProcedure": AbstractProcedure,
    "HecRas": HecRasProcedure,
    "HecRasProcedure": HecRasProcedure,
    "PolynomialTransformationProcedure": PolynomialTransformationProcedure,
    "PolynomialProcedure": PolynomialTransformationProcedure,
    "Polynomial": PolynomialTransformationProcedure,
    "MuskingumChannel": MuskingumChannelProcedure,
    "MuskingumChannelProcedure": MuskingumChannelProcedure,
    "GRP": GRPProcedure,
    "GRPProcedure": GRPProcedure,
    "LinearCombination": LinearCombinationProcedure,
    "LinearCombinationProcedure": LinearCombinationProcedure,
    "LinearCombination2B": LinearCombination2BProcedure,
    "LinearCombination2BProcedure": LinearCombination2BProcedure,
    "LinearCombination3B": LinearCombination3BProcedure,
    "LinearCombination3BProcedure": LinearCombination3BProcedure,
    "LinearCombination4B": LinearCombination4BProcedure,
    "LinearCombination4BProcedure": LinearCombination4BProcedure,
    "Expression": ExpressionProcedure,
    "ExpressionProcedure": ExpressionProcedure,
    "SacramentoSimplified": SacramentoSimplifiedProcedure,
    "SacramentoSimplifiedProcedure": SacramentoSimplifiedProcedure,
    "SacramentoSimplifiedFixedPars": SacramentoSimplifiedFixedParsProcedure,
    "SacramentoSimplifiedFixedParsProcedure": SacramentoSimplifiedFixedParsProcedure,
    "SacEnKF": SacEnkfProcedure,
    "SacEnKFProcedure": SacEnkfProcedure,
    "Junction": JunctionProcedure,
    "JunctionProcedure": JunctionProcedure,
    "LinearChannel": LinearChannelProcedure,
    "LinearChannelProcedure": LinearChannelProcedure,
    "UHLinearChannel": UHLinearChannelProcedure,
    "UHLinearChannelProcedure": UHLinearChannelProcedure,
    "GR4J": GR4JProcedure,
    "GR4JProcedure": GR4JProcedure,
    "GR4J_": GR4J_Procedure,
    "GR4J_Procedure": GR4J_Procedure,
    "HOSH4P1L": HOSH4P1LProcedure,
    "HOSH4P1LProcedure": HOSH4P1LProcedure,
    "HOSH4P1LNash": HOSH4P1LNashProcedure,
    "HOSH4P1LNashProcedure": HOSH4P1LNashProcedure,
    "HOSH4P1LUH": HOSH4P1LUHProcedure,
    "HOSH4P1LUHProcedure": HOSH4P1LUHProcedure,
    "Difference": DifferenceProcedure,
    "DifferenceProcedure": DifferenceProcedure,
    "LinearNet": LinearNetProcedure,
    "LinearNetProcedure": LinearNetProcedure,
    "LinearNet3": LinearNet3Procedure,
    "LinearNet3Procedure": LinearNet3Procedure,
    "ExponentialFit": ExponentialFitProcedure,
    "ExponentialFitProcedure": ExponentialFitProcedure,
    "LinearFit": LinearFitProcedure,
    "LinearFitProcedure": LinearFitProcedure,
    "LagAndRoute": LagAndRouteProcedure,
    "LagAndRouteProcedure": LagAndRouteProcedure,
    "LagAndRouteNet": LagAndRouteNetProcedure,
    "LagAndRouteNetProcedure": LagAndRouteNetProcedure,
    "HIDROSAT": HIDROSATProcedure,
    "HIDROSATProcedure": HIDROSATProcedure,
    "Analogy": AnalogyProcedure,
    "AnalogyProcedure": AnalogyProcedure,
    "Persistence": PersistenceProcedure,
    "PersistenceProcedure": PersistenceProcedure
}

def createProcedure(
        procedure_type : str,
        **kwargs: Any
    ) -> Procedure:
    if procedure_type not in PROCEDURES:
        raise ValueError(f"Invalid procedure_type='{procedure_type}'. Valid values: {','.join(['%s' % k for k in PROCEDURES.keys()])}")
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



