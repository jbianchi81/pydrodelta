from pydrodelta.procedures.linear_net import LinearNetProcedure
from unittest import TestCase
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence

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

class Test_LinearNetProcedure(TestCase):

    def test_direct(self):
        procedure = LinearNetProcedure(
            parameters = {
                "k_1": 2,
                "n_1": 2,
                "k_2": 2,
                "n_2": 2,
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