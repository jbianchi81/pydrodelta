from numpy import array, isnan
from pydrodelta.downhill_simplex import DownhillSimplex
import logging
import os
import json
from pydrodelta.util import tryParseAndLocalizeDate

class Calibration:

    valid_objective_function = ['rmse','mse','bias','stdev_dif','r','nse','cov']

    def __init__(self,procedure,params):
        self.calibrate = bool(params["calibrate"]) if "calibrate" in params else True
        self.procedure = procedure
        self.result_index = params["result_index"] if "result_index" in params else 0
        self.objective_function = params["objective_function"] if "objective_function" in params else 'rmse'
        if self.objective_function not in self.valid_objective_function:
            raise ValueError("objective_function must be one of %s" % ",".join(self.objective_function))
        self.limit = bool(params["limit"]) if "limit" in params else True
        self.sigma = float(params["sigma"]) if "sigma" in params else 0.25
        self.ranges = params["ranges"] if "ranges" in params else None
        self.no_improve_thr = float(params["no_improve_thr"]) if "no_improve_thr" in params else None
        self.max_stagnations = int(params["max_stagnations"]) if "max_stagnations" in params else None
        self.max_iter = int(params["max_iter"])  if "max_iter" in params else None
        self.downhill_simplex = None
        self.simplex = None
        self.calibration_result = None
        self.save_result = params["save_result"] if "save_result" in params else None
        self.calibration_period = self.parseCalibrationPeriod(params["calibration_period"]) if "calibration_period" in params else None

    def parseCalibrationPeriod(self, cal_period) ->tuple:
        if len(cal_period) < 2:
            raise ValueError("calibration_period must be a list of length 2")
        return (
            tryParseAndLocalizeDate(cal_period[0]), 
            tryParseAndLocalizeDate(cal_period[1])
        )
    
    def runReturnScore(self,parameters:array, objective_function:str|None=None, result_index:int|None=None):
        """
        Runs procedure and returned objective function
        procedure.input and procedure.output_obs must be already loaded
        """
        objective_function = objective_function if objective_function is not None else self.objective_function
        result_index = result_index if result_index is not None else self.result_index
        self.procedure.run(
            parameters=parameters, 
            save_results="", 
            load_input=False, 
            load_output_obs=False
        )
        value = getattr(self.procedure.procedure_function_results.statistics[result_index],objective_function)
        logging.debug((parameters, value))
        return value

    def makeSimplex(self,inplace=True, objective_function:str|None=None, result_index:int|None=None,sigma:float|None=None,limit:bool|None=None,ranges:list|None=None) -> list:
        objective_function = objective_function if objective_function is not None else self.objective_function
        if objective_function not in self.valid_objective_function:
            raise ValueError("objective_function must be one of %s" % ",".join(self.objective_function))
        result_index = result_index if result_index is not None else self.result_index
        sigma = sigma if sigma is not None else self.sigma
        limit = limit if limit is not None else self.limit
        ranges = ranges if ranges is not None else self.ranges
        points = self.procedure.function.makeSimplex(sigma=sigma, limit=limit, ranges=ranges)
        simplex = list()
        for i, p in enumerate(points):
            score = self.runReturnScore(parameters=p,objective_function=objective_function, result_index=result_index)
            if score is None:
                raise Exception("Simplex item %i returned None to objective function %s" % (i, objective_function))
            if isnan(score):
                raise Exception("Simplex item %i returned NaN to objective function %s" % (i, objective_function))
            simplex.append( (p, score))
        if inplace:
            self.simplex = array(simplex,dtype=object)
        else:
            return simplex

    def downhillSimplex(self,inplace:bool=True, sigma:int|None=None,limit:bool|None=None,ranges:list|None=None,no_improve_thr:float|None=None, max_stagnations:int|None=None, max_iter:int|None=None):
        sigma = sigma if sigma is not None else self.sigma
        limit = limit if limit is not None else self.limit
        ranges = ranges if ranges is not None else self.ranges
        points = self.procedure.function.makeSimplex(
            sigma=sigma, 
            limit=limit, 
            ranges=ranges
        )
        no_improve_thr = no_improve_thr if no_improve_thr is not None else self.no_improve_thr
        max_stagnations = max_stagnations if max_stagnations is not None else self.max_stagnations
        max_iter = max_iter if max_iter is not None else self.max_iter
        self.procedure.loadInput()
        self.procedure.loadOutputObs()
        downhill_simplex = DownhillSimplex(
            self.runReturnScore, 
            points, 
            no_improve_thr=no_improve_thr, 
            max_stagnations=max_stagnations, 
            max_iter=max_iter
        )
        if inplace:
            self.downhill_simplex = downhill_simplex
        else:
            return downhill_simplex
    def run(self, inplace:bool=True, sigma:int|None=None,limit:bool|None=None,ranges:list|None=None,no_improve_thr:float|None=None, max_stagnations:int|None=None, max_iter:int|None=None, save_result:str|None=None):
        self.downhillSimplex(
            inplace=True, 
            sigma=sigma,
            limit=limit,
            ranges=ranges,
            no_improve_thr=no_improve_thr, 
            max_stagnations=max_stagnations, 
            max_iter=max_iter)
        calibration_result = self.downhill_simplex.run()
        logging.debug("Downhill simplex finished at iteration %i" % self.downhill_simplex.iters)
        save_result = save_result if save_result is not None else self.save_result
        if save_result:
            json.dump(
                {
                    "parameters": list(calibration_result[0]),
                    "score": calibration_result[1]
                },
                open("%s/%s" % (os.environ["PYDRODELTA_DIR"], save_result),"w"),
                indent=4
            )
        if inplace:
            self.calibration_result = calibration_result
        else:
            return calibration_result
        
