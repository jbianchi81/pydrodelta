from pydrodelta.plan import Plan
from unittest import TestCase
from pydrodelta.config import config
from pandas import isnull, DataFrame
from pathlib import Path

data_dir = Path(__file__).parent / "data"

class Test_PQ(TestCase):

    def test_fill_nulls(self):
        plan = Plan.load(data_dir / "plans/dummy_grp_from_csv_one_node_with_nulls.yml")
        self.assertTrue(plan.procedures[0].boundaries.getById("pma").optional)
        plan.execute(upload=False)
        assert isinstance(plan.procedures[0].input, DataFrame)
        self.assertTrue(isnull(plan.procedures[0].input.loc["2023-05-02 00:00:00-03:00","pma"]))
        assert plan.procedures[0].procedure_function_results is not None
        border_conditions = plan.procedures[0].procedure_function_results.toDict()["border_conditions"]
        self.assertEqual(border_conditions[len(border_conditions)-1]["pma"], 0.0)

        