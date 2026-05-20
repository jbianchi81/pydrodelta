from unittest import TestCase
from pydrodelta.plan import Plan
from numpy import isnan
from pathlib import Path
from pydrodelta.procedures.polynomial import PolynomialTransformationProcedure

data_dir = Path(__file__).parent / "data"

class Test_Polynomial(TestCase):

    def test_init(self):
        plan = Plan.load(data_dir / "plans/dummy_polynomial_with_nulls.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        plan.procedures[0].run()
        assert plan.procedures is not None
        assert plan.procedures[0] is not None
        assert plan.procedures[0].output is not None
        self.assertEqual(len(plan.procedures[0].output),1)
        self.assertEqual(len(plan.procedures[0].output[0]),3)
        self.assertTrue(isnan(plan.procedures[0].output[0].loc["2022-07-16T03:00:00.000Z"]["valor"]))
        self.assertRaises(
            Exception, 
            plan.procedures[1].run
        )

    def test_direct(self):
        procedure = PolynomialTransformationProcedure(
            parameters={
                "coefficients": [2],
                "intercept": 1
            },
            boundaries = [
                [1,2,3,4,5]
            ],
            outputs = [[]]
        )
        procedure.run()
        assert procedure.data is not None
        assert len(procedure.data.output.dropna()) == 5
        for i, row in procedure.data.iterrows():
            self.assertAlmostEqual(row.output, row.input * 2 + 1, 7)
        