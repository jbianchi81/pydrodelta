from numpy import array, isnan
from ..downhill_simplex import DownhillSimplex
import logging
import os
import json
from typing import Optional, List, Union, Tuple
from ..descriptors.bool_descriptor import BoolDescriptor
from ..descriptors.int_descriptor import IntDescriptor
from ..descriptors.float_descriptor import FloatDescriptor
from .calibration import Calibration
from ..config import config

class DownhillSimplexCalibration(Calibration):
    """Calibration procedure using Nelder Mead Downhill Simplex"""
    
    limit = BoolDescriptor()
    """Limit values of the parameters to the provided min-max ranges"""

    sigma = FloatDescriptor()
    """Factor of the variance of the initial distribution of the parameter values"""

    @property
    def ranges(self) ->  List[Tuple[float,float]]: 
        """Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)"""
        return self._ranges
    @ranges.setter
    def ranges(
        self,
        ranges : List[Tuple[float,float]]
        ) -> None:
        if ranges is not None:
            if not isinstance(ranges,(list,tuple)):
                raise ValueError("Invalid ranges argument. Must be a list")
            if len(ranges) != len(self._procedure.function._parameters):
                raise ValueError("Invalid ranges argument length. Must be equal the number of parameters of the procedure function (_procedure.function._parameters) =  %i. Instead, length is %i" % (len(self._procedure.function._parameters), len(ranges)))
            self._ranges = list()
            for i, r in enumerate(ranges):
                if not isinstance(r,(list,tuple)):
                    raise ValueError("Invalid ranges argument, item %i: must be a list or tuple. Instead, type is " % (i,type(r)))
                if len(r) < 2:
                    raise ValueError("Invalid ranges argument, item %i must be of length 2. Instead, length is %i " % (i, len(r)))
                self._ranges.append((float(r[0]),float(r[1])))
        else:
            self._ranges = None

    no_improve_thr = FloatDescriptor()
    """break after max_stagnations iterations with an improvement lower than no_improv_thr"""

    max_stagnations = IntDescriptor()
    """break after max_stagnations iterations with an improvement lower than no_improve_thr"""

    max_iter = IntDescriptor()
    """maximum iterations"""

    @property
    def simplex(self) -> List[Tuple[List[float],float]]:
        return self._simplex

    @property
    def downhill_simplex(self) -> DownhillSimplex:
        """Instance of DownhillSimplex"""
        return self._downhill_simplex

    def __init__(
            self,
            procedure,
            calibrate : bool = True,
            result_index : int = 0,
            objective_function : str = 'rmse',
            limit : bool = True,
            sigma : float = 0.25,
            ranges : List[Tuple[float,float]] = None,
            no_improve_thr : float = 0.0000001,
            max_stagnations : int = 10,
            max_iter : int = 5000,
            save_result : str = None,
            calibration_period : list = None
            ):
        """
        Parameters:
        -----------
        procedure : Procedure
            The procedure to be calibrated

        calibrate : bool = True

            Perform the calibration
        
        result_index : int = 0

            Index of the output element to use to compute the objective function

        objective_function : str = 'rmse'

            Objective function for the calibration procedure. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'

        limit : bool = True

            Limit values of the parameters to the provided min-max ranges

        sigma : float = 0.25

            Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range

        ranges : List[Tuple[float,float]] = None

            Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)

        no_improve_thr : float = 0.000001 
        
            break after max_stagnations iterations with an improvement lower than no_improv_thr

        max_stagnations : int = 10
        
            break after max_stagnations iterations with an improvement lower than no_improve_thr

        max_iter : int = 5000

            maximum iterations
        
        save_result : str = None

            Save calibration result into this file
        
        calibration_period : list = None

            Calibration period (begin date, end date) 
        """
        super().__init__(
            procedure = procedure,
            calibrate = calibrate,
            save_result = save_result,
            calibration_period = calibration_period,
            objective_function = objective_function,
            result_index = result_index)
        self.limit = limit
        self.sigma = sigma
        self.ranges = ranges
        self.no_improve_thr = no_improve_thr
        self.max_stagnations = max_stagnations
        self.max_iter = max_iter
        self._downhill_simplex = None
        self._simplex = None

    def toDict(self) -> dict:
        cal_dict = {
            "calibrate": self.calibrate,
            "result_index": self.result_index,
            "objective_function": self.objective_function,
            "limit": self.limit,
            "sigma": self.sigma,
            "ranges": self.ranges,
            "no_improve_thr": self.no_improve_thr,
            "max_stagnations": self.max_stagnations,
            "max_iter": self.max_iter,
            "save_result": self.save_result,
            "calibration_period": [self.calibration_period[0].isoformat(), self.calibration_period[1].isoformat()] if self.calibration_period is not None else None,
            "calibration_result": self.calibration_result,
            "simplex": self.simplex,
            "iters": self._downhill_simplex.iters if self._downhill_simplex is not None else None,
            "limits": self._downhill_simplex.limits if self._downhill_simplex is not None else None
        }
        for key in cal_dict:
            try:
                json.dumps(cal_dict[key])
            except TypeError as e:
                logging.error("calibration['%s'] is not JSON serializable" % key)
                raise(e)
        return cal_dict
    
    def makeSimplex(
        self,
        inplace : bool = True, 
        objective_function : Optional[str] = None, 
        result_index : Optional[int] = None,
        sigma : Optional[float] = None,
        limit : Optional[bool] = None,
        ranges : Optional[List[Tuple[float,float]]] = None
        ) -> Union[None,List[Tuple[List[float],float]]]:
        """Generate simplex
        
        Parameters:
        -----------
        inplace : bool = True

            Save result inplace (self.simplex) and return None. Else return result

        objective_function : Optional[str] = None

            Name of the objective function. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'

        result_index : Optional[int] = None

            Index of the output to use to compute the objective function

        sigma : float = None

            Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range

        limit : bool = True

            Limit values of the parameters to the provided min-max ranges

        ranges : List[Tuple[float,float]] = None

            Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
        
        Returns:
        --------
        None or simplex : Union[None,List[Tuple[List[float],float]]] 

            First element of each item is the parameter list. Second element is the obtained objective function value
        """
        objective_function = objective_function if objective_function is not None else self.objective_function
        if objective_function not in self._valid_objective_function:
            raise ValueError("objective_function must be one of %s" % ",".join(self.objective_function))
        result_index = result_index if result_index is not None else self.result_index
        sigma = sigma if sigma is not None else self.sigma
        limit = limit if limit is not None else self.limit
        ranges = ranges if ranges is not None else self.ranges
        points = self._procedure.function.makeSimplex(sigma=sigma, limit=limit, ranges=ranges)
        simplex = list()
        for i, p in enumerate(points):
            logging.debug("vertex: %s" % str(p))
            score = self.runReturnScore(parameters=p,objective_function=objective_function, result_index=result_index, save_results=self._procedure.save_results)
            if score is None:
                raise Exception("Simplex item %i returned None to objective function %s" % (i, objective_function))
            if isnan(score):
                raise Exception("Simplex item %i returned NaN to objective function %s" % (i, objective_function))
            simplex.append( (p, score))
        if inplace:
            self._simplex = array(simplex,dtype=object)
        else:
            return simplex

    def downhillSimplex(
        self,
        inplace : bool = True, 
        sigma : Optional[int] = None,
        limit : Optional[bool] = None,
        ranges : Optional[List[Tuple[float,float]]] = None,
        no_improve_thr : Optional[float] = None, 
        max_stagnations : Optional[int] = None, 
        max_iter : Optional[int] = None
        ) -> Union[None,DownhillSimplex]:
        """
        Instantiate DownhillSimplex object. Every parameter is optional. If missing or None, the corresponding instance property is used.
        
        Parameters:
        -----------
        inplace : bool = True

            Save result inplace (self.downhill_simplex) and return None. Else return result

        sigma : float = None

            Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range

        limit : bool = True

            Limit values of the parameters to the provided min-max ranges

        ranges : List[Tuple[float,float]] = None

            Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
        
        no_improve_thr : float = None
        
            break after max_stagnations iterations with an improvement lower than no_improv_thr

        max_stagnations : int = None
        
            break after max_stagnations iterations with an improvement lower than no_improve_thr

        max_iter : int = None

            maximum iterations
        
        Returns:
        --------
        None or DownhillSimplex : Union[None,DownhillSimplex]"""
        sigma = sigma if sigma is not None else self.sigma
        limit = limit if limit is not None else self.limit
        ranges = ranges if ranges is not None else self.ranges
        points = self._procedure.function.makeSimplex(
            sigma=sigma, 
            limit=limit, 
            ranges=ranges
        )
        no_improve_thr = no_improve_thr if no_improve_thr is not None else self.no_improve_thr
        max_stagnations = max_stagnations if max_stagnations is not None else self.max_stagnations
        max_iter = max_iter if max_iter is not None else self.max_iter
        self._procedure.loadInputDefault()
        self._procedure.loadOutputObs()
        downhill_simplex = DownhillSimplex(
            self.runReturnScore, 
            points, 
            no_improve_thr=no_improve_thr, 
            max_stagnations=max_stagnations, 
            max_iter=max_iter,
            limit = limit,
            limits = self._procedure.function.limits
        )
        if inplace:
            self._downhill_simplex = downhill_simplex
        else:
            return downhill_simplex
    def run(
        self, 
        inplace : bool = True, 
        sigma : Optional[int] = None,
        limit : Optional[bool] = None,
        ranges : Optional[List[Tuple[float,float]]] = None,
        no_improve_thr : Optional[float] = None, 
        max_stagnations : Optional[int] = None, 
        max_iter : Optional[int] = None,
        save_result : Optional[str] = None
        ) -> Union[None,Tuple[List[float],float]]:
        """
        Execute calibration. Every parameter is optional. If missing or None, the corresponding instance property is used.
        
        Parameters:
        -----------
        inplace : bool = True

            Save result inplace (self.downhill_simplex) and return None. Else return result

        sigma : float = None

            Ratio of the standard deviation of the initial distribution of the parameter values with the min-max range. sigma = stddev / (0.5 * (max_range - min_range)) I.e., if sigma=1, the standard deviation of the parameter values will be equal to half the min-max range

        limit : bool = True

            Limit values of the parameters to the provided min-max ranges

        ranges : List[Tuple[float,float]] = None

            Override default parameter ranges with these values. A list of length equal to the number of parameters of the procedure function (._procedure.function._parameters) where each element is a 2-tuple of floats (range_min, range_max)
        
        no_improve_thr : float = None
        
            break after max_stagnations iterations with an improvement lower than no_improv_thr

        max_stagnations : int = None
        
            break after max_stagnations iterations with an improvement lower than no_improve_thr

        max_iter : int = None

            maximum iterations

        save_results : str = None

            Save the calibration result into this file
        
        Returns:
        --------
        None or calibration result : Tuple[List[float],float]

            First element is the list of calibrated parameters. Second element is the obtained objective function value
        """
        self.downhillSimplex(
            inplace=True, 
            sigma=sigma,
            limit=limit,
            ranges=ranges,
            no_improve_thr=no_improve_thr, 
            max_stagnations=max_stagnations, 
            max_iter=max_iter)
        calibration_result = self._downhill_simplex.run()
        parameters = [float(x) for x in calibration_result[0]]
        score = float(calibration_result[1])
        logging.debug("Downhill simplex finished at iteration %i" % self._downhill_simplex.iters)
        save_result = save_result if save_result is not None else self.save_result
        if save_result:
            json.dump(
                {
                    "parameters": list(parameters),
                    "score": score
                },
                open(
                    os.path.join(
                        config["PYDRODELTA_DIR"], 
                        save_result
                    ),
                    "w"
                ),
                indent = 4
            )
        self.runReturnScore(parameters=parameters, objective_function=self.objective_function)
        self.scores = self._procedure.read_statistics(as_dataframe=True)
        if inplace:
            self._calibration_result = (list(parameters),score)
        else:
            return (parameters, score)
        
