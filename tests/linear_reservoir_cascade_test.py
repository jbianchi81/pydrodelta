from unittest import TestCase
from pydrodelta.pydrology import LinearReservoirCascade
# from numpy import array
# from typing import List, Tuple

class Test_linearreservoircascade(TestCase):

    def test_cascade_rigid(self):
        procedure = LinearReservoirCascade(
            pars = [0.00001, 2],
            Boundaries = [0,1,0,0,0,0,0,0,0,0,0,0,0,0]
        )
        self.assertEqual(procedure.Inflow[1],1)
        procedure.computeOutFlow()
        self.assertAlmostEqual(procedure.Outflow.sum(),1,4)
        self.assertAlmostEqual(procedure.Outflow[1],1,4)
