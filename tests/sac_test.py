from pydrodelta.plan import Plan
from pydrodelta.procedures.sacramento_simplified import SacramentoSimplifiedProcedureFunction
from pydrodelta.util import createDatetimeSequence
from pandas import DataFrame, read_csv
from unittest import TestCase
import yaml
from pydrodelta.config import config
from datetime import datetime, timedelta
from pytz import timezone

class Test_SacramentoSimplified(TestCase):

    def test_calibration_save_result(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        
        self.assertTrue(isinstance(plan.procedures[0].calibration.calibration_result[0],list))
        self.assertEqual(
            len(plan.procedures[0].calibration.calibration_result[0]),
            len(plan.procedures[0].function._parameters)
        )
        for i, value in enumerate(plan.procedures[0].calibration.calibration_result[0]):
            self.assertTrue(isinstance(value,float))
            self.assertTrue(value >= plan.procedures[0].function._parameters[i].min)
            self.assertTrue(value <= plan.procedures[0].function._parameters[i].max)
        plan.procedures[0].calibration.saveResult(
            "results/dummy_sac_cal_result.yml",
            format = "yaml"
        )

        self.assertTrue("scores" in plan.procedures[0].calibration.result)
        self.assertTrue(isinstance(plan.procedures[0].calibration.result["scores"], list))
        self.assertEqual(
            len(plan.procedures[0].calibration.result["scores"]),
            1
        )
        for key in ["n","rmse","r","nse", "n_val", "rmse_val", "r_val", "nse_val"]:
            self.assertTrue(key in plan.procedures[0].calibration.result["scores"][0])
            if key in ["n", "n_val"]:
                self.assertTrue(isinstance(plan.procedures[0].calibration.result["scores"][0][key], int))
            else:
                self.assertTrue(isinstance(plan.procedures[0].calibration.result["scores"][0][key], float))

        saved_result = yaml.load(open("%s/results/dummy_sac_cal_result.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        self.assertTrue("parameters" in saved_result)
        self.assertTrue(isinstance(saved_result["parameters"],list))
        self.assertEqual(
            len(saved_result["parameters"]),
            len(plan.procedures[0].function._parameters)
        )
        for i, value in enumerate(saved_result["parameters"]):
            self.assertTrue(isinstance(value,float))        
            self.assertTrue(value >= plan.procedures[0].function._parameters[i].min)
            self.assertTrue(value <= plan.procedures[0].function._parameters[i].max)

        self.assertTrue("scores" in saved_result)
        self.assertTrue(isinstance(saved_result["scores"], list))
        self.assertEqual(
            len(saved_result["scores"]),
            1
        )

    def test_water_balance(self):
        pf = SacramentoSimplifiedProcedureFunction(
            parameters = {
                "x1_0": 10,
                "x2_0": 10,
                "m1": 1,
                "c1": 0,
                "c2": 0.0001,
                "c3": 0.02,
                "mu": 0,
                "alfa": 0.5,
                "m2": 1,
                "m3": 1
            },
            initial_states = [0, 0, 0, 0],
            extra_pars = {
                "area": 86400000,
                "ae": 1,
                "rho": 0.5,
                "wp": 0.03,
                "fill_nulls": False,
                "no_check1": False,
                "no_check2": False,
                "mock_run": False
            },
            boundaries = [
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
                    "node_variable": [1,40]
                },
                {
                    "name": "smc_obs",
                    "node_variable": [1,20]
                }
            ],
            outputs = [
                {
                    "name": "q_sim",
                    "node_variable": [1,40]
                },
                {
                    "name": "smc_sim",
                    "node_variable": [1,20]
                }
            ]
        )

        # no rain

        input = DataFrame({
            "timestart": createDatetimeSequence(None, timedelta(days=1),datetime(2000,1,1,tzinfo=timezone("UTC")), datetime(2000,1,9,tzinfo=timezone("UTC"))),
            "pma": [0,0,0,0,0,0,0,0],
            "etp": [0,0,0,0,0,0,0,0],
            "q_obs": [0.0,0,0,0,0,0,0,0],
            "smc_obs": [0.0,0,0,0,0,0,0,0]
        })

        output, procedure_results = pf.run(input)

        self.assertEqual(len(output),2)
        self.assertEqual(len(output[0]),8)
        io = pf.results.pma.sum() - pf.results.real_et.sum() - sum(pf.results.x3 * pf.alfa) - sum(pf.results.deep_perc)
        dx = sum(pf.x) - sum(pf.initial_states) 
        self.assertAlmostEqual(
            io,
            dx,
            1,
            "Mass balance failed: input - output: %.1f, delta storage: %.1f" % (io, dx)
        )

        # no rain, initial storage

        pf.initial_states = [5,0,0,0]

        output, procedure_results = pf.run(input)

        io = pf.results.pma.sum() - pf.results.real_et.sum() - sum(pf.results.x3 * pf.alfa) - sum(pf.results.deep_perc)
        dx = sum(pf.x) - sum(pf.initial_states) 
        self.assertAlmostEqual(
            io,
            dx,
            1,
            "Mass balance failed: input - output: %.1f, delta storage: %.1f" % (io, dx)
        )

        # 1 rain pulse

        pf.initial_states = [0,0,0,0]

        input = DataFrame({
            "timestart": createDatetimeSequence(None, timedelta(days=1),datetime(2000,1,1,tzinfo=timezone("UTC")), datetime(2000,1,9,tzinfo=timezone("UTC"))),
            "pma": [5,0,0,0,0,0,0,0],
            "etp": [0,0,0,0,0,0,0,0],
            "q_obs": [0.0,0,0,0,0,0,0,0],
            "smc_obs": [0.0,0,0,0,0,0,0,0]
        })

        output, procedure_results = pf.run(input)

        io = pf.results.pma.sum() - pf.results.real_et.sum() - sum(pf.results.x3 * pf.alfa) - sum(pf.results.deep_perc)
        dx = sum(pf.x) - sum(pf.initial_states) 
        self.assertAlmostEqual(
            io,
            dx,
            1,
            "Mass balance failed: input - output: %.1f, delta storage: %.1f" % (io, dx)
        )
        
        # 1 rain pulse, constant etp

        pf.initial_states = [0,0,0,0]

        input = DataFrame({
            "timestart": createDatetimeSequence(None, timedelta(days=1),datetime(2000,1,1,tzinfo=timezone("UTC")), datetime(2000,1,9,tzinfo=timezone("UTC"))),
            "pma": [5,0,0,0,0,0,0,0],
            "etp": [1,1,1,1,1,1,1,1],
            "q_obs": [0.0,0,0,0,0,0,0,0],
            "smc_obs": [0.0,0,0,0,0,0,0,0]
        })

        output, procedure_results = pf.run(input)

        io = pf.results.pma.sum() - pf.results.real_et.sum() - sum(pf.results.x3 * pf.alfa) - sum(pf.results.deep_perc)
        dx = sum(pf.x) - sum(pf.initial_states) 
        self.assertAlmostEqual(
            io,
            dx,
            0,
            "Mass balance failed: input - output: %.f, delta storage: %.f" % (io, dx)
        )


