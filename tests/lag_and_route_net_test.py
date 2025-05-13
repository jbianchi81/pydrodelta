from pydrodelta.plan import Plan
from pydrodelta.procedures.lag_and_route_net import LagAndRouteNetProcedureFunction
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
from pandas import DataFrame, DatetimeIndex
from pydrodelta.util import createDatetimeSequence

class Test_LagAndRouteNetProcedure(TestCase):

    def test_run(self):
        procedure_function = LagAndRouteNetProcedureFunction(
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
            boundaries = [
                {
                    "name": "input_1",
                    "node_variable": [1,1]
                },
                {
                    "name": "input_2",
                    "node_variable": [2,1]
                },
                {
                    "name": "input_3",
                    "node_variable": [3,1]
                }
            ],
            outputs = [
                {
                    "name": "output",
                    "node_variable": [4,1]
                }
            ]
        )

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

        output, procedure_function_results = procedure_function.run(input_data)
        self.assertEqual(len(output),1)
        self.assertEqual(len(output[0]),31)
        self.assertAlmostEqual(6.06, output[0]["valor"].max(),2)