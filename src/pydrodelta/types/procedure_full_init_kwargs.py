from .procedure_init_kwargs import ProcedureInitKwargs
from typing import List, Any, Mapping, Optional, Union, TypedDict

class ExtraParsDict(TypedDict):
    pass

class ProcedureFullInitKwargs(ProcedureInitKwargs):
    parameters : Union[List[Any], Mapping[str, Any]]
    initial_states: Union[List[Any], Mapping[str, Any]]
    extra_pars: Optional[ExtraParsDict]
    