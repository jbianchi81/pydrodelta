from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
import math
import numpy

class Test_ExponentialFit(TestCase):

    def test_run(self):
        config = yaml.load(open("%s/sample_data/plans/dummy_exponential_fit.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        plan.execute(upload=False)
        self.assertEqual(len(plan.procedures[0].output),1)
        self.assertEqual(len(plan.procedures[0].output[0]),89)
        self.assert_("r2" in plan.procedures[0].function.linear_model)
        self.assert_(plan.procedures[0].function.linear_model["r2"] > 0.99)
        self.assert_("coef" in plan.procedures[0].function.linear_model)
        self.assertEqual(len(plan.procedures[0].function.linear_model["coef"]),1)
        self.assert_("intercept" in plan.procedures[0].function.linear_model)
        self.assertEqual(type(plan.procedures[0].function.linear_model["intercept"]),numpy.float64)
        self.assert_("superior" in plan.procedures[0].output[0])
        self.assert_("inferior" in plan.procedures[0].output[0])
