from unittest import TestCase
from pydrodelta.procedures.junction import JunctionProcedure

class HOSH4P1LTest(TestCase):

    def test_hosh4p1l(self):

        procedure = JunctionProcedure(
          boundaries= [
              [0,80,0,0,0,0,40,0,0,0,0,0,0,0,0,0],
              [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
              [200,180,160,140,160,180,200,180,200,180,160,140,160,180,200,180],
              [0.2,0.18,0.16,0.14,0.16,0.18,0.20,0.18,0.2,0.18,0.16,0.14,0.16,0.18,0.20,0.18],
            ],
            outputs = [
              [200,180,160,140,160,180,200,180,200,180,160,140,160,180,200,180]
            ],
        )

        procedure.run()
        assert len(procedure.outputs)
        assert procedure.data is not None
        assert len(procedure.data.output.dropna()) == 16
        # control balance #
        for i, r in procedure.data.iterrows():
            self.assertAlmostEqual(r.input_1 + r.input_2 + r.input_3 + r.input_4, r.output,2)
            
