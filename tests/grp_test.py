from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
from pathlib import Path

data_dir = Path(__file__).parent / "data"

class Test_GRP(TestCase):

    def test_run(self):
        plan_config = yaml.load(open(data_dir / "plans/dummy_grp_from_csv_one_node.yml"),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        self.assertEqual(len(plan.procedures[0].output[0]),11)

        