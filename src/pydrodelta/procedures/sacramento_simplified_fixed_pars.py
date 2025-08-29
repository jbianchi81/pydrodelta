
from .sacramento_simplified import SacramentoSimplifiedProcedureFunction
from ..model_parameter import ModelParameter
from ..validation import getSchemaAndValidate
from typing import Union
import numpy as np

class SacramentoSimplifiedFixedParsProcedureFunction(SacramentoSimplifiedProcedureFunction):
    """sacramento simplified with fixed soil parameters"""

    # _parameters = [
    #         #  id  | model_id | nombre | lim_inf | range_min | range_max | lim_sup  | orden 
    #         # -----+----------+--------+---------+-----------+-----------+----------+-------
    #     # ModelParameter(name="x1_0",constraints=(1,35,200,np.inf)),
    #     #     #  229 |       27 | x1_0   |       1 |        35 |       200 | Infinity |     1
    #     # ModelParameter(name="x2_0",constraints=(1,33,248,np.inf)),
    #     #     #  230 |       27 | x2_0   |       1 |        33 |       248 | Infinity |     2
    #     # ModelParameter(name="m1",constraints=(1e-09,1,3,np.inf)),
    #     #     #  231 |       27 | m1     |   1e-09 |         1 |         3 | Infinity |     3
    #     # ModelParameter(name="c1",constraints=(1e-09,0.01,0.03,np.inf)),
    #     #     #  232 |       27 | c1     |   1e-09 |      0.01 |      0.03 | Infinity |     4
    #     # ModelParameter(name="c2",constraints=(1e-09,150,500,np.inf)),
    #     #     #  233 |       27 | c2     |   1e-09 |       150 |       500 | Infinity |     5
    #     ModelParameter(name="c3",constraints=(1e-09,0.00044,0.002,np.inf)),
    #         #  234 |       27 | c3     |   1e-09 |   0.00044 |     0.002 | Infinity |     6
    #     ModelParameter(name="mu",constraints=(1e-09,0.4,6,np.inf)),
    #         #  235 |       27 | mu     |   1e-09 |       0.4 |         6 | Infinity |     7
    #     ModelParameter(name="alfa",constraints=(1e-09,0.2,0.3,np.inf)),
    #         #  236 |       27 | alfa   |   1e-09 |       0.2 |       0.3 | Infinity |     8
    #     ModelParameter(name="m2",constraints=(1e-09,1,2.2,np.inf)),
    #         #  237 |       27 | m2     |   1e-09 |         1 |       2.2 | Infinity |     9
    #     ModelParameter(name="m3",constraints=(1e-09,1,5,np.inf))
    #         #  238 |       27 | m3     |   1e-09 |         1 |         5 | Infinity |    10
    # ]

    # @property
    # def x1_0(self) -> float:
    #     """top soil layer storage capacity [L]"""
    #     return self.extra_pars["x1_0"]
    
    # @property
    # def x2_0(self) -> float:
    #     """bottom soil layer storage capacity [L]"""
    #     return self.extra_pars["x2_0"]
    
    # @property
    # def m1(self) -> float:
    #     """runoff function exponent [-]"""
    #     return self.extra_pars["m1"]
    
    # @property
    # def c1(self) -> float:
    #     return self.extra_pars["c1"]
    #     """interflow function coefficient [1/T]"""
        
    # @property
    # def c2(self) -> float:
    #     """percolation function coefficient [-]"""
    #     return self.extra_pars["c2"]
    
    def __init__(
        self,
        parameters : Union[dict,list,tuple],
        initial_states : list,
        fixed_parameters : dict,
        **kwargs
        ):
        """
        parameters : Union[dict,list,tuple]
        
            Properties:
            - c3 : float
                base flow recession rate [1/T]        
            - mu : float
                base flow/deep percolation partition parameter [-]        
            - alfa : float
                linear reservoir coefficient [1/T]        
            - m2 : float
                percolation function exponent [-]        
            - m3
                evapotranspiration function exponent [-]
        
        extra_pars : Union[dict,list,tuple]
        
            - x1_0 : float
                top soil layer storage capacity [L]
            - x2_0 : float
                bottom soil layer storage capacity [L]
            - m1 : float
                runoff function exponent [-]
            - c1 : float
                interflow function coefficient [1/T]        
            - c2 : float
                percolation function coefficient [-]        
            - windowsize : int
                Window size for soil moisture adjustment        
            - dt_sec : int
                Time step in seconds        
            - rho : float
                Soil porosity        
            - ae : float
                Effective area of runnof generation [0-1]        
            - wp : float
                Wilting point        
            - sm_transform : tuple
                soil moisture rescaling parameters (scale, bias)
            - par_fg : dict
                Flood guidance parameters
            - max_npasos : int
                Maximum substeps for model computations        
            - no_check1 : bool
                Perform step subdivision based on precipitation intensity nsteps = pma/2  (for numerical stability)        
            - no_check2 : bool
                Perform step subdivision based on states derivatives (for numerical stability)        
            - rk2 : bool
                Use Runge-Kutta-2 instead of Runge-Kutta-4
        
        initial_states : list
        
                Initial model states (x1,x2,x3,x4)
                """
        kwargs["type"] = "SacramentoSimplified"
        merged_parameters = {
            **parameters,
            **fixed_parameters
        }
            
        super().__init__(
            parameters = merged_parameters, 
            initial_states = initial_states,
            **kwargs) # super(PQProcedureFunction,self).__init__(params,procedure)
        
        reduced_parameters = []
        for p in self._parameters:
            if p.name not in fixed_parameters.keys():
                reduced_parameters.append(p)
        self._parameters = reduced_parameters
        # getSchemaAndValidate(dict(kwargs, parameters = merged_parameters, initial_states = initial_states),"SacramentoSimplifiedProcedureFunction")
        # self.volume = 0
        # self.sm_obs = []
        # self.sm_sim = []
        # self.x = [self.constraint(self.initial_states[i],self._statenames[i]) for i in range(4)]
        # self.X = []
        # self.Xw = []
        # self.flows = None

    def setParameters(
        self, 
        parameters: Union[list,tuple] = ...) -> None:
        super().setParameters(parameters, False)
