# from pydrodelta.procedure import Procedure
from pydrodelta.procedures.abstract import AbstractProcedureFunction
from unittest import TestCase
from pydrodelta.function_boundary import FunctionBoundary

class DummyProcedureFunction(AbstractProcedureFunction):
    _boundaries = [
        FunctionBoundary({"name": "input_1"}),
        FunctionBoundary({"name": "input_2"})
    ]

class Test_Boundaries(TestCase):
    
    def test_raise_missing(self):
        self.assertRaises(
            ValueError,
            DummyProcedureFunction
        )

    def test_create(self):
        procedure_function = DummyProcedureFunction(
            boundaries = [
                {
                    "name": "input_1",
                    "node_variable": [0,0]
                },
                {
                    "name": "input_2",
                    "node_variable": [0,0]
                }
            ]
        )
        self.assertIsInstance(procedure_function, DummyProcedureFunction)

    def test_create_no_boundaries(self):
        p_f = AbstractProcedureFunction()
        self.assertIsInstance(p_f,AbstractProcedureFunction)
