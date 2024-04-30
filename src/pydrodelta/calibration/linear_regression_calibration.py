import logging
from typing import Optional, List, Union, Tuple
from .calibration import Calibration
from ..types.linear_combination_parameters_dict import LinearCombinationParametersDict
import json
from pandas import DataFrame
import os
from datetime import datetime

class LinearRegressionCalibration(Calibration):
    """Calibration procedure using linear regression - least squares"""
    
    def linearRegression(
        self,
        calibration_period : Tuple[datetime,datetime] = None
        ) -> Tuple[LinearCombinationParametersDict,DataFrame] :
        """Perform linear regression

        Args:
            calibration_period : Tuple[datetime,datetime] = None
            Begin and end dates of training set. Data outside this period is used for validation. If not set, validation is not performed
        
        Returns:
            LinearCombinationParametersDict : resulting parameters
            DataFrame : resulting scores"""
        calibration_period = calibration_period if calibration_period is not None else self.calibration_period
        return self._linearRegression(calibration_period=calibration_period)

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

            Ignored. Target series is fixed to the first input

        objective_function : str = 'rmse'

            Ignored. Fixed to rmse

        save_result : str = None

            Save calibration result into this file
        
        calibration_period : Tuple[datetime,datetime] = None

            Begin and end dates of training set. Data outside this period is used for validation. If not set, validation is not performed
        """
        super().__init__(
            procedure = procedure,
            calibrate = calibrate,
            save_result = save_result,
            calibration_period = calibration_period,
            objective_function = "rmse",
            result_index = 0)
        self._linearRegression = getattr(self._procedure.function, "linearRegression", None)
        if not callable(self._linearRegression):
            raise Exception("linear regression not available for this procedure function")

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
    
    def run(
        self, 
        inplace : bool = True, 
        save_result : Optional[str] = None,
        calibration_period : Optional[Tuple[datetime,datetime]] = None
        ) -> Union[None,Tuple[LinearCombinationParametersDict,float]]:
        """
        Execute calibration. Every parameter is optional. If missing or None, the corresponding instance property is used.
        
        Parameters:
        -----------
        inplace : bool = True

            Save result inplace (self._calibration_result) and return None. Else return result

        save_results : str = None

            Save the calibration result into this file

        calibration_period : : Optional[Tuple[datetime,datetime]] = None

            Begin and end dates of training set. Data outside this period is used for validation. If not set, validation is not performed
        
        Returns:
        --------
        None or calibration result : Tuple[List[ForecastStepDict],float]

            First element is the list of calibrated parameters. Second element is the obtained objective function value
        """
        fitted_parameters, results, stats_all = self.linearRegression(calibration_period=calibration_period)
        save_result = save_result if save_result is not None else self.save_result
        if save_result:
            json.dump(
                {
                    "parameters": fitted_parameters,
                    "score": results.to_dict(orient="records")
                },
                open(
                    os.path.join(
                        os.environ["PYDRODELTA_DIR"], 
                        save_result
                    ),
                    "w"
                ),
                indent = 4
            )
        # self.runReturnScore(parameters=fitted_parameters, objective_function=self.objective_function)
        self.scores = results
        self._procedure.function.setParameters(fitted_parameters)
        self._procedure.run()
        if inplace:
            self._calibration_result = (fitted_parameters,results["rmse"][0])
        else:
            return (fitted_parameters,results["rmse"][0])
        
