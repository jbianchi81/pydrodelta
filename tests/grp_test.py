from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os

class Test_GRP(TestCase):

    def test_run(self):
        config = yaml.load(open("%s/sample_data/plans/dummy_grp_from_csv_one_node.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**config)
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        self.assertEqual(len(plan.procedures[0].output[0]),10)

        