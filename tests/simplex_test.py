from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os

class Test_Simplex(TestCase):

    def test_make_simplex(self):
        config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        simplex = plan.procedures[0].function.makeSimplex()
        self.assertTrue(isinstance(simplex,list))
        self.assertEqual(
            len(simplex),
            len(plan.procedures[0].function._parameters) + 1
        )
        for point in simplex:
            self.assertTrue(isinstance(point,list))
            self.assertEqual(
                len(point),
                len(plan.procedures[0].function._parameters)
            )
            for i, value in enumerate(point):
                self.assertTrue(isinstance(value,float))        
                self.assertTrue(value >= plan.procedures[0].function._parameters[i].min)
                self.assertTrue(value <= plan.procedures[0].function._parameters[i].max)