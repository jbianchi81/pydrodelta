from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
import math
import numpy
from pydrodelta.procedure import Procedure
from pydrodelta.types.enhanced_typed_list import EnhancedTypedList
from pydrodelta.procedure_boundary import ProcedureBoundary
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

    def test_boundaries(self):
        procedure = Procedure(
            "dummy exponential fit",
            {
                "type": "ExponentialFit",
                "boundaries": [
                    {
                        "name": "input",
                        "node_variable": [1,40]
                    }
                ],
                "outputs": [
                    {
                        "name": "output",
                        "node_variable": [1,39]
                    }
                ]
            }
        )
        self.assertIsInstance(procedure.function.boundaries, EnhancedTypedList)
        self.assertEquals(len(procedure.function.boundaries),1)
        self.assertIsInstance(procedure.function.boundaries.getById("input"),ProcedureBoundary)
        self.assertRaises(
            ValueError,
            procedure.function.boundaries.append,
            {
                "name": "eenpoot",
                "node_variable": [1,40]
            }
        )
        self.assertRaises(
            ValueError,
            procedure.function.boundaries.append,
            {
                "name": "input",
                "node_variable": [1,40]
            }
        )


        i = procedure.function.boundaries.getIndex("input")
        self.assertRaises(
            AttributeError,
            setattr,
            procedure.function.boundaries[i],
            "node_id",
            14
        )
        self.assertRaises(
            AttributeError,
            setattr,
            procedure.function.boundaries[i],
            "var_id",
            44
        )
    
    def test_replace_boundaries(self):
        procedure = Procedure(
            "dummy exponential fit",
            {
                "type": "ExponentialFit",
                "boundaries": [
                    {
                        "name": "input",
                        "node_variable": [1,40]
                    }
                ],
                "outputs": [
                    {
                        "name": "output",
                        "node_variable": [1,39]
                    }
                ]
            }
        )
        boundaries = procedure.function.boundaries
        self.assertEquals(len(boundaries),1)
        boundaries.replace(
            0,
            {
                "name": "input",
                "node_variable": [2,41]
            }
        )
        self.assertEquals(boundaries[0].node_id,2)
        self.assertEquals(boundaries[0].var_id,41)
    
    def test_missing_boundaries(self):
        self.assertRaises(
            ValueError,
            Procedure,
            "dummy exponential fit",
            {
                "type": "ExponentialFit",
                "boundaries": [],
                "outputs": [
                    {
                        "name": "output",
                        "node_variable": [1,39]
                    }
                ]
            }
        )
    
    def test_assert_missing_ids(self):
        procedure = Procedure(
            "dummy exponential fit",
            {
                "type": "ExponentialFit",
                "boundaries": [
                    {
                        "name": "input",
                        "node_variable": [1,40]
                    }
                ],
                "outputs": [
                    {
                        "name": "output",
                        "node_variable": [1,39]
                    }
                ]
            }
        )
        procedure.function.boundaries.assert_missing_ids()
        procedure.function.outputs.assert_missing_ids()

    