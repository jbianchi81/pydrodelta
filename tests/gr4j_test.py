from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
import numpy as np
from pydrodelta.procedures.gr4j import GR4JProcedureFunction
from pydrodelta.pydrology import GR4J

class Test_GR4J(TestCase):

    def test_prodstore_runoff(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_gr4j.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)

        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        self.assertIsInstance(plan.procedures[0].function, GR4JProcedureFunction)
        self.assertIsInstance(plan.procedures[0].function.engine, GR4J)
        self.assertEqual(plan.procedures[0].function.engine.prodStoreMaxStorage,100)
        self.assertEqual(plan.procedures[0].function.engine.T,1)
        self.assertEqual(plan.procedures[0].function.engine.routStoreMaxStorage,10)
        self.assertEqual(plan.procedures[0].function.engine.waterExchange,0)
        self.assertAlmostEqual(np.sum(plan.procedures[0].function.engine.u1),1)
        self.assertAlmostEqual(np.sum(plan.procedures[0].function.engine.u2),1)
        self.assertEqual(len(plan.procedures[0].output[0]),11)
        Recharge_0 = 100 * np.tanh(1)
        SoilStorage_1_ =  0 + Recharge_0 - 0
        relativeMoisture = SoilStorage_1_/100
        Infiltration_0 = SoilStorage_1_  * (1-(1+(4/9*relativeMoisture)**4)**(-1/4))
        Runoff_0 = Infiltration_0 + 100 - Recharge_0
        self.assertAlmostEqual(plan.procedures[0].function.engine.prodStore.Infiltration[0],Infiltration_0)
        self.assertAlmostEqual(plan.procedures[0].function.engine.prodStore.SoilStorage[1], SoilStorage_1_ - Infiltration_0)
        self.assertAlmostEqual(plan.procedures[0].function.engine.prodStore.Runoff[0],Runoff_0)
        # self.assertAlmostEqual(np.sum(plan.procedures[0].function.engine.routStore.Runoff),0)
        # self.assertEqual(np.sum(plan.procedures[0].function.engine.Runoff),0)
        # self.assertEqual(np.sum(plan.procedures[0].function.engine.Q),0)