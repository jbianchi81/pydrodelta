from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pydrodelta.config import config
from pandas import DataFrame
from pathlib import Path
from pydrodelta.procedures.lag_and_route import LagAndRouteProcedureFunction

data_dir = Path(__file__).parent / "data"

class Test_LagAndRouteProcedure(TestCase):

    def test_run(self):
        plan = Plan.load(data_dir / "plans/lar_dummy.yml")
        pf = plan.procedures[0].function
        assert isinstance(pf, LagAndRouteProcedureFunction)
        self.assertEqual(pf.pars_list[0], 3)
        self.assertTrue(pf.pars_list[1], 0.5)
        self.assertTrue(pf.pars_list[2], 2)
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        plan.execute(upload=False)
        pr = plan.procedures[0]
        assert pr.output is not None
        self.assertGreaterEqual(len(pr.output[0]),31)
        assert pr.procedure_function_results is not None
        assert isinstance(pr.procedure_function_results.data,DataFrame)
        self.assertTrue("output" in pr.procedure_function_results.data)
        self.assertEqual(len(pr.procedure_function_results.data["output"].dropna()), 31)

    def test_run_no_output(self):
        plan = Plan.load(data_dir / "plans/lar_dummy_no_output.yml")
        plan.execute(upload=False)
        pr = plan.procedures[0]
        assert pr.output is not None
        self.assertGreaterEqual(len(pr.output[0]),31)
        assert pr.procedure_function_results is not None
        self.assertEqual(type(pr.procedure_function_results.data),DataFrame)
        assert isinstance(pr.procedure_function_results.data, DataFrame)
        self.assertTrue("output" in pr.procedure_function_results.data)
        self.assertEqual(len(pr.procedure_function_results.data["output"].dropna()), 31)



