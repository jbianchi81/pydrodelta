from unittest import TestCase
from pydrodelta.procedures.hosh4p1l import HOSH4P1LProcedure

class HOSH4P1LTest(TestCase):

  procedure : HOSH4P1LProcedure

  @classmethod
  def setUpClass(cls):
    cls.procedure = HOSH4P1LProcedure(
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
          "distribution": "Symmetric",
          "k": 0.5,
          "maxSoilStorage": 200,
          "maxSurfaceStorage": 200,
          "n": 2,
          "Proc": "UH",
          "T": 3.2
        }
    )

  def test_01_hosh4p1l(self):
    self.procedure.run()
    assert len(self.procedure.outputs)
    assert self.procedure.data is not None
    assert len(self.procedure.data.q_sim.dropna()) == 16

  def test_02_control_balance(self):
    initial_storage = self.procedure.engine.SoilStorage[0] + self.procedure.engine.SurfaceStorage[0]
    final_storage = self.procedure.engine.SoilStorage[-1] + self.procedure.engine.SurfaceStorage[-1]
    gain = sum(self.procedure.engine.Precipitation)
    loss = sum(self.procedure.engine.EVR1) + sum(self.procedure.engine.EVR2) + sum(self.procedure.engine.Q)
    self.assertAlmostEqual(initial_storage + gain - loss, final_storage,2)