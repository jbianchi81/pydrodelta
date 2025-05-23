from pydrodelta.plan import Plan
from pydrodelta.procedure import Procedure
from unittest import TestCase
import yaml
import os
import math
from pydrodelta.config import config

class Test_LinearCombination(TestCase):

    def test_run(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lc_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        self.assertEqual(len(plan.procedures[0].output[0]),3)

    def test_calibrate(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lc_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        fitted_parameters, results, stats_all = plan.procedures[0].function.linearRegression()
        self.assertEqual(plan.procedures[0].function.parameters["forecast_steps"], fitted_parameters["forecast_steps"])
        self.assertEqual(plan.procedures[0].function.parameters["lookback_steps"], fitted_parameters["lookback_steps"])
        self.assertEqual(plan.procedures[0].function.parameters["forecast_steps"], len(fitted_parameters["coefficients"]))
        for i, step in enumerate(fitted_parameters["coefficients"]):
            self.assertEqual(i, step["step"])
            self.assertTrue(isinstance(step["intercept"],(float,int)))
            self.assertFalse(math.isnan(step["intercept"]))
            self.assertEqual(len(plan.procedures[0].function.boundaries), len(step["boundaries"]))
            for j, boundary in enumerate(step["boundaries"]):
                self.assertEqual(plan.procedures[0].function.boundaries[j].name, boundary["name"])
                self.assertEqual(plan.procedures[0].function.parameters["lookback_steps"], len(boundary["values"]))
                for k, value in enumerate(boundary["values"]):
                    self.assertTrue(isinstance(step["intercept"],(float,int)))
                    self.assertFalse(math.isnan(value))

    def test_calibrate_results(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lc_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        fitted_parameters, results, stats_all = plan.procedures[0].function.linearRegression()
        self.assertEqual(plan.procedures[0].function.parameters["forecast_steps"], len(results))
        for i, step in enumerate(fitted_parameters["coefficients"]):
            self.assertEqual(i, int(results["horiz"][i]))
            n = len(plan.procedures[0].loadInput(inplace=False)[0]) - plan.procedures[0].function.parameters["lookback_steps"] - i
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
        plan_config = yaml.load(open("%s/sample_data/plans/lc_dummy_cal.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        plan.procedures[0].calibration.run()
        self.assertEqual(len(plan.procedures[0].calibration.scores),3)
        for i, step in enumerate(plan.procedures[0].calibration.calibration_result[0]["coefficients"]):
            self.assertEqual(i, int(plan.procedures[0].calibration.scores["horiz"][i]))
            n = len(plan.procedures[0].loadInput(inplace=False)[0]) - plan.procedures[0].function.parameters["lookback_steps"] - plan.procedures[0].calibration.scores["n_val"][i] - i
            self.assertEqual(n, int(plan.procedures[0].calibration.scores["n"][i]))
            if i == 0:
                self.assertTrue(plan.procedures[0].calibration.scores["r"][i] >= 0.98)
                self.assertTrue(plan.procedures[0].calibration.scores["nse"][i] >= 0.98)
            else:
                self.assertTrue(plan.procedures[0].calibration.scores["rmse"][i] > plan.procedures[0].calibration.scores["rmse"][i-1])
                self.assertTrue(plan.procedures[0].calibration.scores["r"][i] < plan.procedures[0].calibration.scores["r"][i-1])
                self.assertTrue(plan.procedures[0].calibration.scores["nse"][i] < plan.procedures[0].calibration.scores["nse"][i-1])
                self.assertTrue(plan.procedures[0].calibration.scores["rmse_val"][i] > plan.procedures[0].calibration.scores["rmse_val"][i-1])
                self.assertTrue(plan.procedures[0].calibration.scores["r_val"][i] < plan.procedures[0].calibration.scores["r_val"][i-1])
                self.assertTrue(plan.procedures[0].calibration.scores["nse_val"][i] < plan.procedures[0].calibration.scores["nse_val"][i-1])

    def test_calibration_exec(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lc_dummy_cal.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        fitted_parameters = plan.procedures[0].calibration.calibration_result[0]

        self.assertTrue("coefficients" in fitted_parameters)
        self.assertTrue("forecast_steps" in fitted_parameters)
        self.assertEqual(fitted_parameters["forecast_steps"], len(fitted_parameters["coefficients"]))
        self.assertEqual(len(plan.topology.nodes[1].variables[40].series_sim[0].data), 3)
        
    def test_calibration_save_result(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lc_dummy_cal.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        plan.procedures[0].calibration.saveResult("results/lc_dummy_result.yml", format="yaml")
        saved_result = yaml.load(open("%s/results/lc_dummy_result.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        self.assertTrue("parameters" in saved_result)
        self.assertEqual(saved_result["parameters"]["forecast_steps"], plan.procedures[0].function.parameters["forecast_steps"])
        self.assertEqual(saved_result["parameters"]["lookback_steps"], plan.procedures[0].function.parameters["lookback_steps"])
        self.assertEqual(len(saved_result["parameters"]["coefficients"]), len(plan.procedures[0].function.parameters["coefficients"]))
    
    def test_assert_missing_parameters(self):
        self.assertRaises(
            TypeError,
            Procedure,
            1,
            {
                "type": "LinearCombination"
            }
        )
