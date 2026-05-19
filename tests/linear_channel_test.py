from pydrodelta.procedures.linear_channel import LinearChannelProcedure
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

class Test_LinearChannelProcedure(TestCase):

    def test_run(self):
        procedure = LinearChannelProcedure(
            parameters = {"n": 3, "k": 2},
            boundaries = input_data,
            outputs = [[]]
        )

        procedure.run()
        assert procedure.data is not None
        output = procedure.data.output
        self.assertIsNotNone(output)
        self.assertAlmostEqual(max(output),1.01,2)
