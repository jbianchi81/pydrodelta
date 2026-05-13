# from pydrodelta.procedure import Procedure
from pydrodelta.procedure import Procedure
from unittest import TestCase
from pydrodelta.function_boundary import FunctionBoundary

class DummyProcedure(Procedure):
    _boundaries = [
        FunctionBoundary({"name": "input_1"}),
        FunctionBoundary({"name": "input_2"})
    ]

class Test_Boundaries(TestCase):
    
    def test_raise_missing(self):
        self.assertRaises(
            ValueError,
            DummyProcedure
        )

    def test_create(self):
        procedure_function = DummyProcedure(
            boundaries = [
                {
                    "name": "input_1",
                    "node_variable": (0,0)
                },
                {
                    "name": "input_2",
                    "node_variable": (0,0)
                }
            ]
        )
        self.assertIsInstance(procedure_function, DummyProcedure)

    def test_create_no_boundaries(self):
        procedure = Procedure()
        self.assertIsInstance(procedure,Procedure)
