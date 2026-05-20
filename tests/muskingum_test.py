from pydrodelta.procedures.muskingumchannel import MuskingumChannelProcedure
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

class Test_MuskingumChannelProcedure(TestCase):

    def test_run(self):
        procedure = MuskingumChannelProcedure(
            parameters = {"K": 2, "X": 0.5},
            boundaries = input_data,
            outputs = [[]]
        )

        procedure.run()
        assert procedure.data is not None
        output = procedure.data.output
        self.assertIsNotNone(output)
        self.assertAlmostEqual(max(output),1.01,2)
