from unittest import TestCase
from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedure
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence
import numpy as np

class HOSH4P1LTest(TestCase):

    def test_hoshp1l(self):

        procedure = HOSH4P1LProcedure(
          boundaries= [
              [0,0,0,0,80,0,0,0],
              [1,1,1,1,1,1,1,1],
              [200,180,160,140,160,180,200,180],
              [0.2,0.18,0.16,0.14,0.16,0.18,0.20,0.18],
            ],
            extra_pars = {
                "dt": 1,
                "area": 1000000000,
                "ae": 1,
                "rho": 0.5,
                "wp": 0.03,
                "approx": False,
                "fill_nulls": False,
                "shift": False
            },
            initial_states = {
                "SoilStorage": 0.1,
                "SurfaceStorage": 0.1
            },
            outputs = [
              [200,180,160,140,160,180,200,180],
              [0.2,0.18,0.16,0.14,0.16,0.18,0.20,0.18]
            ],
            parameters = {
              "distribution": "Symmetric",
              "k": 1,
              "maxSoilStorage": 200,
              "maxSurfaceStorage": 200,
              "n": 2,
              "Proc": "UH",
              "T": 1.2
            }
        )

        procedure.exec()
        assert len(procedure.outputs)