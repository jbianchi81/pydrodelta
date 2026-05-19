from pydrodelta.procedures.lag_and_route_net import LagAndRouteNetProcedure
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
    DataFrame(
        {
            "valor": [2.02] * 31
        },
        index = index
    ),
    DataFrame(
        {
            "valor": [3.03] * 31
        },
        index = index
    )
]

class Test_LagAndRouteNetProcedure(TestCase):

    def test_run(self):
        boundaries : List[ProcedureBoundaryDict] = [
            {
                "name": "input_1",
                "node_variable": (1,1)
            },
            {
                "name": "input_2",
                "node_variable": (2,1)
            },
            {
                "name": "input_3",
                "node_variable": (3,1)
            }
        ]
        procedure = LagAndRouteNetProcedure(
            parameters = {
                "lag_1": 2,
                "k_1": 2,
                "n_1": 2,
                "lag_2": 2,
                "k_2": 2,
                "n_2": 2,
                "lag_3": 2,
                "k_3": 2,
                "n_3": 2
            },
            boundaries = boundaries,
            outputs = [
                {
                    "name": "output",
                    "node_variable": (4,1)
                }
            ]
        )

        output, procedure_function_results = procedure.exec(input_data)
        self.assertEqual(len(output),1)
        self.assertEqual(len(output[0]),31)
        self.assertAlmostEqual(6.06, output[0]["valor"].max(),2)

    def test_direct(self):
        procedure = LagAndRouteNetProcedure(
            parameters = {
                "lag_1": 2,
                "k_1": 2,
                "n_1": 2,
                "lag_2": 2,
                "k_2": 2,
                "n_2": 2,
                "lag_3": 2,
                "k_3": 2,
                "n_3": 2
            },
            extra_pars = {
                "dt": 1
            },
            boundaries = input_data,
            outputs = [
                []
            ]
        )
        procedure.run()
        assert procedure.data is not None
        self.assertEqual(len(procedure.data),31)
        self.assertAlmostEqual(6.06, procedure.data["output"].max(),2)