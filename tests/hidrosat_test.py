from unittest import TestCase
from pydrodelta.procedures.hidrosat import HIDROSATProcedureFunction
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence
import numpy as np

class HidrosatTest(TestCase):

    def test_hidrosat(self):

        pf = HIDROSATProcedureFunction(
          boundaries= [
            {
              "name": "pma",
              "node_variable": [1,1]
            },
            {
              "name": "etp",
              "node_variable": [1,15]
            },
            {
              "name": "q_obs",
              "node_variable": [1, 40]  
            },
            {
              "name": "smc_obs",
              "node_variable": [1, 20]
            }
            ],
            extra_pars = {
                "dt": 1,
                "area": 1000000000,
                "ae": 1,
                "rho": 0.5,
                "wp": 0.03
            },
            initial_states = {
                "soilStorage":100,
                "Runoff": 0,
                "floodPlainStorage": 0,
                "Flooded": 0.001
            },
            outputs = [
                {
                "name": "q_sim",
                "node_variable": [1, 40]
                },
                {
                "name": "smc_sim",
                "node_variable": [1, 20]
                }
            ],
            parameters = {
                "K": 1,
                "N": 3,
                "Q0": 12.69,
                "S0": 178.395,
                "W0": 232.505,
                "gamma": 2.28,
                "maxFlooded": 0.09
            },
            type = "HIDROSAT"
        )
        dti = createDatetimeSequence(timeInterval={"days":1}, timestart=(2000,1,1), timeend=(2001,1,4))
        output, results = pf.run([
            DataFrame(index=dti, data={"valor":[10,0,0,0,0,15,0,0,0,0] * 37}),
            DataFrame(index=dti, data={"valor":[2] * 370}),
            DataFrame(index=dti, data={"valor":[np.nan] * 370}),
            DataFrame(index=dti, data={"valor":[np.nan] * 370}),
        ])
        self.assertEqual(len(output),2)
        self.assertEqual(len(output[0]),len(dti))
        self.assertAlmostEqual(pf.engine.soilStorage[0] + pf.engine.floodplainStorage[0] + pf.engine.Precipitation.sum() - pf.engine.EVSoil.sum() - pf.engine.EVFloodPlain.sum() - pf.engine.Q[:-1].sum(), pf.engine.soilStorage[len(dti)-1] + pf.engine.floodplainStorage[len(dti)-1],2)


