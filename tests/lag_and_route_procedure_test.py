from pydrodelta.procedures.lag_and_route import LagAndRouteProcedure
from unittest import TestCase
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence
from typing import List
from pydrodelta.types.procedure_boundary_dict import ProcedureBoundaryDict

index = createDatetimeSequence(
    timestart = "2000-01-01", 
    timeend = "2000-01-31"
)

input_data = [
    DataFrame(
        {
            "valor": [1.01] * 31
        },
        index = index
    ),
]

class Test_LagAndRouteProcedure(TestCase):

    def test_run(self):
        procedure = LagAndRouteProcedure(
            parameters = {"n": 3, "k": 2, "lag": 1},
            initial_states = [0],
            extra_pars = {"dt": 1},
            boundaries = input_data,
            outputs = [[]]
        )

        procedure.run()
        assert procedure.data is not None
        output = procedure.data.output
        self.assertIsNotNone(output)
        self.assertAlmostEqual(max(output),1.01,2)
