from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
import numpy as np
from pydrodelta.procedures.gr4j import GR4JProcedure
from pydrodelta.pydrology import GR4J
from pathlib import Path

data_dir = Path(__file__).parent / "data"

class Test_GR4J(TestCase):

    def test_prodstore_runoff(self):
        plan = Plan.load(data_dir / "plans/dummy_gr4j.yml")

        assert plan.topology is not None
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        procedure = plan.procedures[0]
        assert isinstance(procedure,GR4JProcedure)
        self.assertIsInstance(procedure.engine, GR4J)
        self.assertEqual(procedure.engine.prodStoreMaxStorage,100)
        self.assertEqual(procedure.engine.T,1)
        self.assertEqual(procedure.engine.routStoreMaxStorage,10)
        self.assertEqual(procedure.engine.waterExchange,0)
        self.assertAlmostEqual(np.sum(procedure.engine.u1),1)
        self.assertAlmostEqual(np.sum(procedure.engine.u2),1)
        assert procedure.output is not None
        self.assertEqual(len(procedure.output[0]),11)
        Recharge_0 = 100 * np.tanh(1)
        SoilStorage_1_ =  0 + Recharge_0 - 0
        relativeMoisture = SoilStorage_1_/100
        Infiltration_0 = SoilStorage_1_  * (1-(1+(4/9*relativeMoisture)**4)**(-1/4))
        Runoff_0 = Infiltration_0 + 100 - Recharge_0
        self.assertAlmostEqual(procedure.engine.prodStore.Infiltration[0],Infiltration_0)
        self.assertAlmostEqual(procedure.engine.prodStore.SoilStorage[1], SoilStorage_1_ - Infiltration_0)
        self.assertAlmostEqual(procedure.engine.prodStore.Runoff[0],Runoff_0)
        # self.assertAlmostEqual(np.sum(pf.engine.routStore.Runoff),0)
        # self.assertEqual(np.sum(pf.engine.Runoff),0)
        # self.assertEqual(np.sum(pf.engine.Q),0)