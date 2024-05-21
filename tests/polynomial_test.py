from unittest import TestCase
from pydrodelta.plan import Plan
from numpy import isnan

class Test_Polynomial(TestCase):

    def test_init(self):
        plan = Plan.load("sample_data/plans/dummy_polynomial_with_nulls.yml")
        plan.topology.batchProcessInput()
        plan.procedures[0].run()
        self.assertEquals(len(plan.procedures[0].output),1)
        self.assertEquals(len(plan.procedures[0].output[0]),3)
        self.assertTrue(isnan(plan.procedures[0].output[0].loc["2022-07-16T03:00:00.000Z"]["valor"]))
        self.assertRaises(
            Exception, 
            plan.procedures[1].run
        )
        