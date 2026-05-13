from unittest import TestCase
from pydrodelta.procedures.hidrosat import HIDROSATProcedure
from pandas import DataFrame
from pydrodelta.util import createDatetimeSequence
import numpy as np

class HidrosatTest(TestCase):

    def test_hidrosat(self):

        procedure = HIDROSATProcedure(
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
                "soilStorage":0,
                "Runoff": 0,
                "floodPlainStorage": 0,
                "Flooded": 0
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
        output, results = procedure.exec([
            DataFrame(index=dti, data={"valor":[10,0,0,0,0,15,0,0,0,0] * 37}),
            DataFrame(index=dti, data={"valor":[2] * 370}),
            # DataFrame(index=dti, data={"valor":[np.nan] * 370}),
            # DataFrame(index=dti, data={"valor":[np.nan] * 370}),
        ])
        self.assertEqual(len(output),2)
        self.assertEqual(len(output[0]),len(dti))
        s_i = procedure.engine.soilStorage[0] + procedure.engine.floodplainStorage[0]
        s_f = procedure.engine.soilStorage[len(dti)-1] + procedure.engine.floodplainStorage[len(dti)-1] # + pf.engine.routingSystem.Storage[1]
        i_o = procedure.engine.Precipitation.sum() - procedure.engine.EVSoil.sum() - procedure.engine.EVFloodPlain.sum() - procedure.engine.Q[:-1].sum()

        self.assertAlmostEqual((s_f - s_i) * 0.1, i_o * 0.1, 0)


    def test_hidrosat_init_soil(self):

        procedure = HIDROSATProcedure(
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
                "soilStorage":10,
                "Runoff": 0,
                "floodPlainStorage": 0,
                "Flooded": 0
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
        output, results = procedure.exec([
            DataFrame(index=dti, data={"valor":[10,0,0,0,0,15,0,0,0,0] * 37}),
            DataFrame(index=dti, data={"valor":[2] * 370}),
            # DataFrame(index=dti, data={"valor":[np.nan] * 370}),
            # DataFrame(index=dti, data={"valor":[np.nan] * 370}),
        ])
        self.assertEqual(len(output),2)
        self.assertEqual(len(output[0]),len(dti))
        s_i = procedure.engine.soilStorage[0] + procedure.engine.floodplainStorage[0]
        s_f = procedure.engine.soilStorage[len(dti)-1] + procedure.engine.floodplainStorage[len(dti)-1] # + pf.engine.routingSystem.Storage[1]
        i_o = procedure.engine.Precipitation.sum() - procedure.engine.EVSoil.sum() - procedure.engine.EVFloodPlain.sum() - procedure.engine.Q[:-1].sum()

        self.assertAlmostEqual((s_f - s_i) * 0.1, i_o * 0.1, 0)

        mass_balance = procedure.massBalance()

        self.assertAlmostEqual(mass_balance["discrepancy"]*0.1,0,0)


