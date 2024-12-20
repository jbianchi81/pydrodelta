from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pandas import DataFrame
from pydrodelta.types.typed_list import TypedList
from pydrodelta.procedure import Procedure
from pydrodelta.procedures.abstract import AbstractProcedureFunction
from pydrodelta.config import config

class Test_Plan(TestCase):

    def test_init(self):
        read_stream = open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        self.assertEqual(plan.name,"linear_channel_dummy")
        self.assertEqual(plan.id, 505)
        self.assertEqual(plan.forecast_date.isoformat(), "2024-01-03T00:00:00-03:00")
        self.assertEqual(len(plan.topology.nodes),2)
        self.assertEqual(len(plan.procedures),1)

    def test_analysis(self):
        read_stream = open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        for n in plan.topology.nodes:
            for v in n.variables:
                self.assertTrue(isinstance(n.variables[v].data,DataFrame))
                self.assertEqual(len(n.variables[v].data),14)
                self.assertEqual(min(n.variables[v].data.index).isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(n.variables[v].data.index).isoformat(),"2024-01-14T00:00:00-03:00")

    def test_exec(self):
        read_stream = open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        for p in plan.procedures:
            for i in p.input:
                self.assertTrue(isinstance(i,DataFrame))
                self.assertEqual(len(i),14)
                self.assertEqual(min(i.index).isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(i.index).isoformat(),"2024-01-14T00:00:00-03:00")
            for o in p.output:
                self.assertTrue(isinstance(o,DataFrame))
                self.assertEqual(len(o),14)
                self.assertEqual(min(o.index).isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(o.index).isoformat(),"2024-01-14T00:00:00-03:00")
        for s in plan.topology.nodes[1].variables[40].series_sim:
            self.assertTrue(isinstance(s.data,DataFrame))
            self.assertEqual(len(s.data),14)
            self.assertEqual(min(s.data.index).isoformat(),"2024-01-01T00:00:00-03:00")
            self.assertEqual(max(s.data.index).isoformat(),"2024-01-14T00:00:00-03:00")
            self.assertAlmostEqual(
                plan.topology.nodes[0].variables[40].data["valor"].sum(skipna=True),
                sum(s.data["valor"]), 
                places = 1)
    
    def test_api(self):
        read_stream = open("%s/sample_data/plans/dummy_polynomial.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput(
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })
        for n in plan.topology.nodes:
            for v in n.variables:
                self.assertTrue(isinstance(n.variables[v].data,DataFrame))
                self.assertEqual(len(n.variables[v].data),3)
                self.assertEqual(min(n.variables[v].data.index).isoformat(),"2022-07-15T00:00:00-03:00")
                self.assertEqual(max(n.variables[v].data.index).isoformat(),"2022-07-17T00:00:00-03:00")

    def test_api_basin_pars(self):
        read_stream = open("%s/sample_data/plans/dummy_sac_basin_pars_from_api.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        self.assertTrue("area" in plan.procedures[0].function.extra_pars)
        self.assertIsNotNone(plan.procedures[0].function.extra_pars["area"])
        self.assertAlmostEqual(plan.procedures[0].function.extra_pars["area"], 140273473.449287,0)
        plan.execute(
            upload = False
        )
        
    def test_api_exec(self):
        read_stream = open("%s/sample_data/plans/dummy_polynomial.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.execute(
            upload = False,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })

    def test_calibration(self):
        read_stream = open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.execute(upload = False)
        stats = plan.procedures[0].read_statistics()
        self.assertEqual(stats["results"][0]["n"], 3)
        self.assertEqual(stats["results"][1]["n"], 3)
        self.assertEqual(stats["results_val"][0]["n"], 2)
        self.assertEqual(stats["results_val"][1]["n"], 2)
        calibration = plan.procedures[0].calibration.toDict()
        self.assertEqual(len(calibration["calibration_result"][0]),10)
        for i, x in enumerate(calibration["calibration_result"][0]):
            self.assertEqual(x, plan.procedures[0].function.parameter_list[i])
        self.assertEqual(calibration["calibration_result"][1], stats["results"][0]["oneminusr"])
        self.assertEqual(len(calibration["limits"]),10)

    def test_stats_df(self):
        read_stream = open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.procedures[0].calibration.calibrate = False
        plan.execute(upload = False)
        stats_df = plan.procedures[0].read_statistics(as_dataframe=True)
        self.assertTrue(isinstance(stats_df, DataFrame))

    def test_stats_df_score(self):
        read_stream = open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        plan.execute(upload = False)
        self.assertTrue(isinstance(plan.procedures[0].calibration.scores, DataFrame))

    def test_calibration_save_result_raise_exception(self):
        read_stream = open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"])
        plan_config = yaml.load(read_stream,yaml.CLoader)
        read_stream.close()
        plan = Plan(**plan_config)
        self.assertRaises(
            Exception, 
            plan.procedures[0].calibration.saveResult,
            "results/dummy_sac_cal_result.json"
        )
        # plan.execute(upload = False)
    
    def test_append_procedure(self):
        plan = Plan(
            "plan 0",
            123,
            {
                "timestart": "2000-01-01T12:00:00.000Z",
                "timeend": "2000-01-06T12:00:00.000Z",
                "time_offset": { "hours": 9},
                "nodes": []
            }
        )
        self.assertIsInstance(
            plan.procedures,
            TypedList
        )
        procedure = Procedure(
            1,
            {
                "type": "ProcedureFunction"
            }
        )
        plan.procedures.append(procedure)

    def test_duplicate_procedure(self):
        plan = Plan(
            "plan 0",
            123,
            {
                "timestart": "2000-01-01T12:00:00.000Z",
                "timeend": "2000-01-06T12:00:00.000Z",
                "time_offset": { "hours": 9},
                "nodes": []
            },
            procedures = [
                {
                    "id": 1,
                    "function": {
                        "type": "AbstractProcedureFunction",
                        "parameters": [],
                        "boundaries": [],
                        "outputs": []                        
                    }
                }
            ]
        )
        self.assertIsInstance(
            plan.procedures,
            TypedList
        )
        procedure = Procedure(
            1,
            {
                "type": "AbstractProcedureFunction",
                "parameters": [],
                "boundaries": [],
                "outputs": []                        
            }
        )
        self.assertRaises(
            ValueError,
            plan.procedures.append,
            procedure
        )

        
