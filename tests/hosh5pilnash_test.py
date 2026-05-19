from unittest import TestCase
from pydrodelta.procedures.hosh4p1lnash import HOSH4P1LNashProcedure

class HOSH4P1LNashTest(TestCase):

    def test_hosh4p1lnash(self):

        procedure = HOSH4P1LNashProcedure(
          boundaries= [
              [0,80,0,0,0,0,40,0,0,0,0,0,0,0,0,0],
              [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
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
                "SoilStorage": 150,
                "SurfaceStorage": 150
            },
            outputs = [
              [200,180,160,140,160,180,200,180],
              [0.2,0.18,0.16,0.14,0.16,0.18,0.20,0.18]
            ],
            parameters = {
              "k": 0.5,
              "maxSoilStorage": 200,
              "maxSurfaceStorage": 200,
              "n": 2,
            }
        )

        procedure.run()
        assert len(procedure.outputs)
        assert procedure.data is not None
        assert len(procedure.data.q_sim.dropna()) == 16
        # control balance #
        initial_storage = procedure.engine.SoilStorage[0] + procedure.engine.SurfaceStorage[0]
        final_storage = procedure.engine.SoilStorage[-1] + procedure.engine.SurfaceStorage[-1]
        gain = sum(procedure.engine.Precipitation)
        loss = sum(procedure.engine.EVR1) + sum(procedure.engine.EVR2) + sum(procedure.engine.Q)
        self.assertAlmostEqual(initial_storage + gain - loss, final_storage,2)