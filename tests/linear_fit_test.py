from pydrodelta.plan import Plan
from unittest import TestCase
class Test_LinearFit(TestCase):

    def test_run(self):
        plan = Plan.load("sample_data/plans/dummy_linear_fit_2_boundaries.yml")
        plan.execute(upload=False)
