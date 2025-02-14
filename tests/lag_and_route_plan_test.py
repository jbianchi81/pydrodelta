from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
from pandas import DataFrame

class Test_LagAndRouteProcedure(TestCase):

    def test_run(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lar_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        self.assertEqual(plan.procedures[0].function.pars_list[0], 3)
        self.assertTrue(plan.procedures[0].function.pars_list[1], 0.5)
        self.assertTrue(plan.procedures[0].function.pars_list[2], 2)
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        self.assertGreaterEqual(len(plan.procedures[0].output[0]),31)
        self.assertEqual(type(plan.procedures[0].procedure_function_results.data),DataFrame)
        self.assertTrue("output" in plan.procedures[0].procedure_function_results.data)
        self.assertEqual(len(plan.procedures[0].procedure_function_results.data["output"].dropna()), 31)

    def test_run_no_output(self):
        plan_config = yaml.load(open("%s/sample_data/plans/lar_dummy_no_output.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        self.assertGreaterEqual(len(plan.procedures[0].output[0]),31)
        self.assertEqual(type(plan.procedures[0].procedure_function_results.data),DataFrame)
        self.assertTrue("output" in plan.procedures[0].procedure_function_results.data)
        self.assertEqual(len(plan.procedures[0].procedure_function_results.data["output"].dropna()), 31)



