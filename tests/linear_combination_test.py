from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
import math

class Test_LinearCombination(TestCase):

    def test_run(self):
        config = yaml.load(open("%s/sample_data/plans/lc_dummy.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        plan.execute(upload=False)
        self.assertEqual(len(plan.procedures[0].output[0]),3)

    def test_calibrate(self):
        config = yaml.load(open("%s/sample_data/plans/lc_dummy.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        plan.topology.batchProcessInput()
        fitted_parameters, results, stats_all = plan.procedures[0].function.calibrate()
        self.assertEqual(plan.procedures[0].function.parameters["forecast_steps"], fitted_parameters["forecast_steps"])
        self.assertEqual(plan.procedures[0].function.parameters["lookback_steps"], fitted_parameters["lookback_steps"])
        self.assertEqual(plan.procedures[0].function.parameters["forecast_steps"], len(fitted_parameters["coefficients"]))
        for i, step in enumerate(fitted_parameters["coefficients"]):
            self.assertEqual(i, step["step"])
            self.assert_(isinstance(step["intercept"],(float,int)))
            self.assertFalse(math.isnan(step["intercept"]))
            self.assertEqual(len(plan.procedures[0].function.boundaries), len(step["boundaries"]))
            for j, boundary in enumerate(step["boundaries"]):
                self.assertEqual(plan.procedures[0].function.boundaries[j].name, boundary["name"])
                self.assertEqual(plan.procedures[0].function.parameters["lookback_steps"], len(boundary["values"]))
                for k, value in enumerate(boundary["values"]):
                    self.assert_(isinstance(step["intercept"],(float,int)))
                    self.assertFalse(math.isnan(value))

    def test_calibrate_results(self):
        config = yaml.load(open("%s/sample_data/plans/lc_dummy.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        plan.topology.batchProcessInput()
        fitted_parameters, results, stats_all = plan.procedures[0].function.calibrate()
        self.assertEqual(plan.procedures[0].function.parameters["forecast_steps"], len(results))
        for i, step in enumerate(fitted_parameters["coefficients"]):
            self.assertEqual(i, int(results["horiz"][i]))
            n = len(plan.procedures[0].loadInput(inplace=False)[0]) - plan.procedures[0].function.parameters["lookback_steps"] - i
            self.assertEqual(n, int(results["n"][i]))
            if i == 0:
                self.assert_(results["r"][i] >= 0.99)
                self.assert_(results["nse"][i] >= 0.99)
            else:
                self.assert_(results["rmse"][i] > results["rmse"][i-1])
                self.assert_(results["r"][i] < results["r"][i-1])
                self.assert_(results["nse"][i] < results["nse"][i-1])
