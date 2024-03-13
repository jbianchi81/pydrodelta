from numpy import array
import logging
import json
from ..util import tryParseAndLocalizeDate
from typing import Optional, List, Union, Tuple
from datetime import datetime
from ..descriptors.bool_descriptor import BoolDescriptor
from ..descriptors.int_descriptor import IntDescriptor
from ..descriptors.string_descriptor import StringDescriptor

class Calibration:
    """Calibration base/abstract class"""
    
    _valid_objective_function = ['rmse','mse','bias','stdev_dif','r','nse','cov',"oneminusr"]

    calibrate = BoolDescriptor()
    """Perform the calibration"""

    result_index = IntDescriptor()
    """Index of the result element to use to compute the objective function"""

    objective_function = StringDescriptor()
    """
    Objective function for the calibration procedure. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr' 
    """

    @property
    def calibration_result(self) -> Tuple[List[float],float]:
        """Calibration result. First element is the list of obtained parameters. The second element is the obtained objective function value"""
        return self._calibration_result

    save_result = StringDescriptor()
    """Save calibration result into this file"""

    @property
    def calibration_period(self) -> Tuple[datetime, datetime]:
        """Calibration period (begin date, end date)"""
        return self._calibration_period
    @calibration_period.setter
    def calibration_period(
        self,
        calibration_period : Tuple[Union[datetime,dict,float], Union[datetime,dict,float]]
        ) -> None:
        self._calibration_period = self.parseCalibrationPeriod(calibration_period) if calibration_period is not None else None

    def __init__(
            self,
            procedure,
            calibrate : bool = True,
            result_index : int = 0,
            objective_function : str = 'rmse',
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

        save_result : str = None

            Save calibration result into this file
        
        calibration_period : list = None

            Calibration period (begin date, end date) 
        """
        self._procedure = procedure
        self.calibrate = calibrate
        self.result_index = result_index
        self.objective_function = objective_function
        if self.objective_function not in self._valid_objective_function:
            raise ValueError("objective_function must be one of %s" % ",".join(self._valid_objective_function))
        self._calibration_result = None
        self.save_result = save_result
        self.calibration_period = calibration_period

    def toDict(self) -> dict:
        cal_dict = {
            "calibrate": self.calibrate,
            "result_index": self.result_index,
            "objective_function": self.objective_function,
            "save_result": self.save_result,
            "calibration_period": [self.calibration_period[0].isoformat(), self.calibration_period[1].isoformat()] if self.calibration_period is not None else None,
            "calibration_result": self.calibration_result
        }
        for key in cal_dict:
            try:
                json.dumps(cal_dict[key])
            except TypeError as e:
                logging.error("calibration['%s'] is not JSON serializable" % key)
                raise(e)
        return cal_dict
    
    def parseCalibrationPeriod(
        self, 
        cal_period : Tuple[Union[datetime,dict,float], Union[datetime,dict,float]]
        ) -> Tuple[datetime, datetime]:
        if len(cal_period) < 2:
            raise ValueError("calibration_period must be a list of length 2")
        return (
            tryParseAndLocalizeDate(cal_period[0]), 
            tryParseAndLocalizeDate(cal_period[1])
        )
    
    def runReturnScore(
        self,
        parameters : array, 
        objective_function : Optional[str] = None, 
        result_index : Optional[int] = None,
        save_results : str = None,
        ) -> float:
        """
        Runs procedure and returns objective function value
        procedure.input and procedure.output_obs must be already loaded

        Parameters:
        -----------
        parameters : array

            Procedure function parameters

        objective_function : Optional[str] = None

            Name of the objective function. One of 'rmse', 'mse', 'bias', 'stdev_dif', 'r', 'nse', 'cov', 'oneminusr'

        result_index : Optional[int] = None

            Index of the output to use to compute the objective function

        Returns:
        --------
        the objective function value : float
        """
        objective_function = objective_function if objective_function is not None else self.objective_function
        result_index = result_index if result_index is not None else self.result_index
        self._procedure.run(
            parameters=parameters, 
            save_results=save_results, 
            load_input=False, 
            load_output_obs=False
        )
        value = getattr(self._procedure.procedure_function_results.statistics[result_index],objective_function)
        logging.debug((parameters, value))
        return value

    def run(
        self, 
        inplace : bool = True, 
        save_result : Optional[str] = None,
        **kwargs
        ) -> Union[None,Tuple[List[float],float]]:
        """
        Execute calibration. Every parameter is optional. If missing or None, the corresponding instance property is used.
        
        Parameters:
        -----------
        inplace : bool = True

            Save result inplace (self.downhill_simplex) and return None. Else return result

        save_results : str = None

            Save the calibration result into this file
        
        Returns:
        --------
        None or calibration result : Tuple[List[float],float]

            First element is the list of calibrated parameters. Second element is the obtained objective function value
        """
        raise NotImplementedError("run() method not implemented for the base class Calibration. It must be overriden by the derived class")
        
