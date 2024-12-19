from pydrodelta.plan import Plan
from unittest import TestCase
from pydrodelta.config import config
from pandas import isnull

class Test_PQ(TestCase):

    def test_fill_nulls(self):
        plan = Plan.load("%s/sample_data/plans/dummy_grp_from_csv_one_node_with_nulls.yml" % config["PYDRODELTA_DIR"])
        self.assertTrue(plan.procedures[0].function.boundaries.getById("pma").optional)
        plan.execute(upload=False)
        self.assertTrue(isnull(plan.procedures[0].input.loc["2023-05-02 00:00:00-03:00","pma"]))
        border_conditions = plan.procedures[0].procedure_function_results.toDict()["border_conditions"]
        self.assertEquals(border_conditions[len(border_conditions)-1]["pma"], 0.0)

        