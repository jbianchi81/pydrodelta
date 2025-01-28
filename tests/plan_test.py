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
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        self.assertEqual(plan.name,"linear_channel_dummy")
        self.assertEqual(plan.id, 505)
        self.assertEqual(plan.forecast_date.isoformat(), "2024-01-03T00:00:00-03:00")
        self.assertEqual(len(plan.topology.nodes),2)
        self.assertEqual(len(plan.procedures),1)

    def test_analysis(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.topology.batchProcessInput()
        for n in plan.topology.nodes:
            for v in n.variables:
                self.assertTrue(isinstance(n.variables[v].data,DataFrame))
                self.assertEqual(len(n.variables[v].data),15)
                self.assertEqual(min(n.variables[v].data.index).isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(n.variables[v].data.index).isoformat(),"2024-01-15T00:00:00-03:00")

    def test_exec(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload=False)
        for p in plan.procedures:
            for i in p.input:
                self.assertTrue(isinstance(i,DataFrame))
                self.assertEqual(len(i),15)
                self.assertEqual(min(i.index).isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(i.index).isoformat(),"2024-01-15T00:00:00-03:00")
            for o in p.output:
                self.assertTrue(isinstance(o,DataFrame))
                self.assertEqual(len(o),15)
                self.assertEqual(min(o.index).isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(o.index).isoformat(),"2024-01-15T00:00:00-03:00")
        for s in plan.topology.nodes[1].variables[40].series_sim:
            self.assertTrue(isinstance(s.data,DataFrame))
            self.assertEqual(len(s.data),15)
            self.assertEqual(min(s.data.index).isoformat(),"2024-01-01T00:00:00-03:00")
            self.assertEqual(max(s.data.index).isoformat(),"2024-01-15T00:00:00-03:00")
            self.assertAlmostEqual(
                plan.topology.nodes[0].variables[40].data["valor"].sum(skipna=True),
                sum(s.data["valor"]), 
                places = 1)
    
    def test_api(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_polynomial.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
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
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_sac_basin_pars_from_api.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        self.assertTrue("area" in plan.procedures[0].function.extra_pars)
        self.assertIsNotNone(plan.procedures[0].function.extra_pars["area"])
        self.assertAlmostEqual(plan.procedures[0].function.extra_pars["area"], 140273473.449287,1)
        plan.execute(
            upload = False
        )
        
    def test_api_exec(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_polynomial.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(
            upload = False,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })

    def test_calibration(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
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
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.procedures[0].calibration.calibrate = False
        plan.execute(upload = False)
        stats_df = plan.procedures[0].read_statistics(as_dataframe=True)
        self.assertTrue(isinstance(stats_df, DataFrame))

    def test_stats_df_score(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan = Plan(**plan_config)
        plan.execute(upload = False)
        self.assertTrue(isinstance(plan.procedures[0].calibration.scores, DataFrame))

    def test_calibration_save_result_raise_exception(self):
        plan_config = yaml.load(open("%s/sample_data/plans/dummy_sac.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
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

    def test_nan(self):
        plan = Plan(
            name = "test_nan",
            id = 111,
            topology = {
                "timestart": "2000-01-01T03:00:00.000Z",
                "timeend": "2000-01-05T03:00:00.000Z",
                "nodes":  [
                    {
                        "id": 0,
                        "name": "node_0",
                        "time_interval": {
                            "days": 1
                        },
                        "node_type": "station",
                        "variables": [
                            {
                                "id": 40,
                                "series": [
                                    {
                                        "series_id": 100,
                                        "observations": [ 
                                            [ "2000-01-01T03:00:00.000Z", 1011.111],
                                            [ "2000-01-02T03:00:00.000Z", 1012.111],
                                            [ "2000-01-03T03:00:00.000Z", 1013.111],
                                            [ "2000-01-04T03:00:00.000Z", 1014.111],
                                            [ "2000-01-05T03:00:00.000Z", 1015.111]
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": 1,
                        "name": "node_1",
                        "time_interval": {
                            "days": 1
                        },
                        "node_type": "station",
                        "variables": [
                            {
                                "id": 40,
                                "series": [
                                    {
                                        "series_id": 101,
                                        "observations": [ 
                                            [ "2000-01-01T03:00:00.000Z", 2011.111],
                                            [ "2000-01-02T03:00:00.000Z", 2012.111],
                                            [ "2000-01-03T03:00:00.000Z", 2013.111],
                                            [ "2000-01-04T03:00:00.000Z", 2014.111],
                                            [ "2000-01-05T03:00:00.000Z", 2015.111]
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "name": "node_2",
                        "time_interval": {
                            "days": 1
                        },
                        "node_type": "station",
                        "variables": [
                            {
                                "id": 40,
                                "series": [
                                    {
                                        "series_id": 102,
                                        "observations": [ 
                                            [ "2000-01-01T03:00:00.000Z", 3011.111],
                                            [ "2000-01-02T03:00:00.000Z", 3012.111],
                                            [ "2000-01-03T03:00:00.000Z", 3013.111]
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "name": "node_3",
                        "time_interval": {
                            "days": 1
                        },
                        "node_type": "station",
                        "variables": [
                            {
                                "id": 40,
                                "series_sim": [
                                    {
                                        "series_id": 103
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            procedures = [
                {
                    "id": "Yacyretá/Pilco - Corrientes",
                    "adjust": True,
                    "warmup_steps": 20,
                    "tail_steps": 60,
                    "function": {
                        "type": "LinearNet3",
                        "boundaries": [
                            {
                                "name": "input_1",
                                "node_variable": [
                                    0,
                                    40
                                ]
                            },
                            {
                                "name": "input_2",
                                "node_variable": [
                                    1,
                                    40
                                ]
                            },
                            {
                                "name": "input_3",
                                "node_variable": [
                                    2,
                                    40
                                ]
                            }
                        ],
                        "outputs": [
                            {
                                "name": "output",
                                "node_variable": [
                                    3,
                                    40
                                ]
                            }
                        ],
                        "parameters": {
                            "k_1": 3,
                            "n_1": 2,
                            "k_2": 5,
                            "n_2": 2,
                            "k_3": 2.45,
                            "n_3": 2
                        }
                    }
                }
            ],
            forecast_date = "2000-01-03T03:00:00.000Z",
            time_interval = {"days": 1}
        )
        self.assertEqual(plan.name,"test_nan")
        self.assertEqual(plan.id, 111)
        self.assertEqual(plan.forecast_date.isoformat(), "2000-01-03T00:00:00-03:00")
        self.assertEqual(len(plan.topology.nodes),4)
        self.assertEqual(len(plan.procedures),1)
        
        plan.topology.batchProcessInput()

        procedure = plan.procedures[0]
        self.assertRaises(
            Exception,
            procedure.loadInput,
            message = "expected raised exception"
        )
        # procedure.loadInput()
        # self.assertEqual(
        #     len(procedure.function.boundaries[2]._variable.data),
        #     5, 
        #     "expected length 5, got %i" % len(procedure.function.boundaries[2]._variable.data))
        # self.assertEqual(
        #     len(procedure.function.boundaries[2]._variable.data.dropna()),
        #     3, 
        #     "expected length 3, got %s " % procedure.function.boundaries[2]._variable.data.dropna())
        
        # self.assertRaises(
        #     AssertionError,
        #     procedure.function.boundaries[2].assertNoNaN,
        #     message="expected to raise AssertionError"
        # )

    def test_save_variable(self):
        plan_config = yaml.load(open("%s/sample_data/plans/linear_channel_dummy.yml" % config["PYDRODELTA_DIR"]),yaml.CLoader)
        plan_config["topology"]["save_variable"] = [
            {
                "var_id": 40,
                "output": "%s/results/q_data.csv" % config["PYDRODELTA_DIR"],
                "format": "csv",
                "pivot": True
            }
        ]
        plan = Plan(
            **plan_config
        )
        plan.execute(upload=False)

