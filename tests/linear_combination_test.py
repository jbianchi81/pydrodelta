from pydrodelta.plan import Plan
from pydrodelta.procedure import Procedure
from unittest import TestCase
import yaml
import os
import math
from pydrodelta.config import config
from pathlib import Path
from pydrodelta.procedures.linear_combination import LinearCombinationProcedureFunction

data_dir = Path(__file__).parent / "data"

class Test_LinearCombination(TestCase):

    def test_run(self):
        plan = Plan.load(data_dir / "plans/lc_dummy.yml")
        plan.execute(upload=False)
        pr = plan.procedures[0]
        assert pr.output is not None
        self.assertEqual(len(pr.output[0]),3)

    def test_calibrate(self):
        plan = Plan.load(data_dir / "plans/lc_dummy.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        pr = plan.procedures[0]
        assert isinstance(pr.function,LinearCombinationProcedureFunction)
        fitted_parameters, results, stats_all = pr.function.linearRegression()
        self.assertEqual(pr.function.parameters["forecast_steps"], fitted_parameters["forecast_steps"])
        self.assertEqual(pr.function.parameters["lookback_steps"], fitted_parameters["lookback_steps"])
        self.assertEqual(pr.function.parameters["forecast_steps"], len(fitted_parameters["coefficients"]))
        for i, step in enumerate(fitted_parameters["coefficients"]):
            self.assertEqual(i, step["step"])
            self.assertTrue(isinstance(step["intercept"],(float,int)))
            self.assertFalse(math.isnan(step["intercept"]))
            self.assertEqual(len(pr.function.boundaries), len(step["boundaries"]))
            for j, boundary in enumerate(step["boundaries"]):
                self.assertEqual(pr.function.boundaries[j].name, boundary["name"])
                self.assertEqual(pr.function.parameters["lookback_steps"], len(boundary["values"]))
                for k, value in enumerate(boundary["values"]):
                    self.assertTrue(isinstance(step["intercept"],(float,int)))
                    self.assertFalse(math.isnan(value))

    def test_calibrate_results(self):
        plan = Plan.load(data_dir / "plans/lc_dummy.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        pr = plan.procedures[0]
        assert isinstance(pr.function, LinearCombinationProcedureFunction)
        fitted_parameters, results, stats_all = pr.function.linearRegression()
        self.assertEqual(pr.function.parameters["forecast_steps"], len(results))
        for i, step in enumerate(fitted_parameters["coefficients"]):
            self.assertEqual(i, int(results["horiz"][i]))
            n = len(pr.loadInput(inplace=False)[0]) - pr.function.parameters["lookback_steps"] - i
            self.assertEqual(n, int(results["n"][i]))
            if i == 0:
                self.assertTrue(results["r"][i] >= 0.99)
                self.assertTrue(results["nse"][i] >= 0.99)
                self.assertTrue(results["rse"][i] < 21.0)
            else:
                self.assertTrue(results["rmse"][i] > results["rmse"][i-1])
                self.assertTrue(results["r"][i] < results["r"][i-1])
                self.assertTrue(results["nse"][i] < results["nse"][i-1])
                self.assertTrue(results["rse"][i] >= results["rse"][i-1])


    def test_calibration_period(self):
        plan = Plan.load(data_dir / "plans/lc_dummy_cal.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        pr = plan.procedures[0]
        assert pr.calibration is not None
        pr.calibration.run()
        self.assertEqual(len(pr.calibration.scores),3)
        assert pr.calibration.calibration_result is not None
        cr = pr.calibration.calibration_result[0]
        assert isinstance(pr.function.parameters, dict)
        for i, step in enumerate(cr["coefficients"]):
            self.assertEqual(i, int(pr.calibration.scores["horiz"][i]))
            n = len(pr.loadInput(inplace=False)[0]) - pr.function.parameters["lookback_steps"] - pr.calibration.scores["n_val"][i] - i
            self.assertEqual(n, int(pr.calibration.scores["n"][i]))
            if i == 0:
                self.assertTrue(pr.calibration.scores["r"][i] >= 0.98)
                self.assertTrue(pr.calibration.scores["nse"][i] >= 0.98)
            else:
                self.assertTrue(pr.calibration.scores["rmse"][i] > pr.calibration.scores["rmse"][i-1])
                self.assertTrue(pr.calibration.scores["r"][i] < pr.calibration.scores["r"][i-1])
                self.assertTrue(pr.calibration.scores["nse"][i] < pr.calibration.scores["nse"][i-1])
                self.assertTrue(pr.calibration.scores["rmse_val"][i] > pr.calibration.scores["rmse_val"][i-1])
                self.assertTrue(pr.calibration.scores["r_val"][i] < pr.calibration.scores["r_val"][i-1])
                self.assertTrue(pr.calibration.scores["nse_val"][i] < pr.calibration.scores["nse_val"][i-1])

    def test_calibration_exec(self):
        plan = Plan.load(data_dir / "plans/lc_dummy_cal.yml")
        plan.execute(upload=False)
        pr = plan.procedures[0]
        assert pr.calibration is not None
        assert pr.calibration.calibration_result is not None
        fitted_parameters = pr.calibration.calibration_result[0]

        self.assertTrue("coefficients" in fitted_parameters)
        self.assertTrue("forecast_steps" in fitted_parameters)
        self.assertEqual(fitted_parameters["forecast_steps"], len(fitted_parameters["coefficients"]))
        assert plan.topology is not None
        n = plan.topology.nodes[1]
        v = n.variables[40]
        assert v.series_sim is not None
        self.assertEqual(len(v.series_sim[0].data), 3)
        
    def test_calibration_save_result(self):
        plan = Plan.load(data_dir / "plans/lc_dummy_cal.yml")
        plan.execute(upload=False)
        pr = plan.procedures[0]
        assert pr.calibration is not None
        pr.calibration.saveResult(data_dir / "results/lc_dummy_result.yml", format="yaml")
        saved_result = yaml.load(open(data_dir / "results/lc_dummy_result.yml"),yaml.CLoader)
        self.assertTrue("parameters" in saved_result)
        assert isinstance(pr.function.parameters, dict)
        self.assertEqual(saved_result["parameters"]["forecast_steps"], pr.function.parameters["forecast_steps"])
        self.assertEqual(saved_result["parameters"]["lookback_steps"], pr.function.parameters["lookback_steps"])
        self.assertEqual(len(saved_result["parameters"]["coefficients"]), len(pr.function.parameters["coefficients"]))
    
    def test_assert_missing_parameters(self):
        self.assertRaises(
            TypeError,
            Procedure,
            1,
            {
                "type": "LinearCombination"
            }
        )
