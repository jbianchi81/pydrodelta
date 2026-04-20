from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
from pathlib import Path

data_dir = Path(__file__).parent / "data"

class Test_GRP(TestCase):

    def test_run(self):
        plan = Plan.load(data_dir / "plans/dummy_grp_from_csv_one_node.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        pr = plan.procedures[0]
        assert pr.output is not None
        self.assertEqual(len(pr.output[0]),11)

        