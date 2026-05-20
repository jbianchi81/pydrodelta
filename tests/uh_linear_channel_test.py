from pydrodelta.procedures.uh_linear_channel import UHLinearChannelProcedure
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
]

class Test_UHLinearChannelProcedure(TestCase):

    def test_run(self):
        procedure = UHLinearChannelProcedure(
            parameters = {"u": [0.1,0.8,0.1]},
            boundaries = input_data,
            outputs = [[]]
        )

        procedure.run()
        assert procedure.data is not None
        output = procedure.data.output
        self.assertIsNotNone(output)
        self.assertAlmostEqual(max(output),1.01,2)
