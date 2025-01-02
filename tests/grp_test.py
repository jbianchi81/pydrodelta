from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config

class Test_GRP(TestCase):

    def test_run(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_grp_from_csv_one_node.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        self.assertEqual(len(plan.procedures[0].output[0]),11)

        