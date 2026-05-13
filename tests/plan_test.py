from pydrodelta.plan import Plan
from unittest import TestCase
import yaml
import os
from pandas import DataFrame
from pydrodelta.types.typed_list import TypedList
from pydrodelta.procedure import Procedure
from pydrodelta.procedures.abstract import AbstractProcedure
from pydrodelta.config import config
from pathlib import Path
from pydrodelta.custom_errors import DuplicateKeyError

data_dir = Path(__file__).parent / "data"

class Test_Plan(TestCase):

    def test_init(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        self.assertEqual(plan.name,"linear_channel_dummy")
        self.assertEqual(plan.id, 505)
        self.assertEqual(plan.forecast_date.isoformat(), "2024-01-03T00:00:00-03:00")
        assert plan.topology is not None
        self.assertEqual(len(plan.topology.nodes),2)
        self.assertEqual(len(plan.procedures),1)

    def test_analysis(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput()
        for n in plan.topology.nodes:
            for v in n.variables:
                self.assertTrue(isinstance(n.variables[v].data,DataFrame))
                self.assertEqual(len(n.variables[v].data),15)
                self.assertEqual(min(n.variables[v].data.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(n.variables[v].data.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-15T00:00:00-03:00")

    def test_exec(self):
        plan = Plan.load(data_dir / "plans/linear_channel_dummy.yml")
        plan.execute(upload=False)
        for p in plan.procedures:
            assert p.input is not None
            for i in p.input:
                self.assertTrue(isinstance(i,DataFrame))
                assert isinstance(i, DataFrame)
                self.assertEqual(len(i),15)
                self.assertEqual(min(i.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(i.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-15T00:00:00-03:00")
            assert p.output is not None
            for o in p.output:
                self.assertTrue(isinstance(o,DataFrame))
                assert isinstance(o, DataFrame)
                self.assertEqual(len(o),15)
                self.assertEqual(min(o.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-01T00:00:00-03:00")
                self.assertEqual(max(o.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-15T00:00:00-03:00")
        assert plan.topology is not None
        assert plan.topology.nodes is not None
        assert plan.topology.nodes[1].variables[40].series_sim is not None
        for s in plan.topology.nodes[1].variables[40].series_sim:
            self.assertTrue(isinstance(s.data,DataFrame))
            self.assertEqual(len(s.data),15)
            self.assertEqual(min(s.data.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-01T00:00:00-03:00")
            self.assertEqual(max(s.data.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2024-01-15T00:00:00-03:00")
            self.assertAlmostEqual(
                plan.topology.nodes[0].variables[40].data["valor"].sum(skipna=True),
                sum(s.data["valor"]), 
                places = 1)
    
    def test_api(self):
        plan = Plan.load(data_dir / "plans/dummy_polynomial.yml")
        assert plan.topology is not None
        plan.topology.batchProcessInput(
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            })
        for n in plan.topology.nodes:
            for v in n.variables:
                self.assertTrue(isinstance(n.variables[v].data,DataFrame))
                self.assertEqual(len(n.variables[v].data),3)
                self.assertEqual(min(n.variables[v].data.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2022-07-15T00:00:00-03:00")
                self.assertEqual(max(n.variables[v].data.index).tz_convert("America/Argentina/Buenos_Aires").isoformat(),"2022-07-17T00:00:00-03:00")

    def test_api_basin_pars(self):
        plan = Plan.load(data_dir / "plans/dummy_sac_basin_pars_from_api.yml")
        self.assertTrue("area" in plan.procedures[0].extra_pars)
        self.assertIsNotNone(plan.procedures[0].extra_pars["area"])
        self.assertAlmostEqual(plan.procedures[0].extra_pars["area"], 45250735227.4144,1)
        plan.execute(
            upload = False
        )
        
    def test_api_exec(self):
        plan = Plan.load(data_dir / "plans/dummy_polynomial.yml")
        plan.execute(
            upload = False,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            })

    def test_calibration(self):
        plan = Plan.load(data_dir / "plans/dummy_sac.yml")
        plan.execute(upload = False)
        stats = plan.procedures[0].read_statistics()
        assert stats["results"] is not None
        assert stats["results"][0] is not None
        self.assertEqual(stats["results"][0]["n"], 3)
        assert stats["results"][1] is not None
        self.assertEqual(stats["results"][1]["n"], 3)
        assert stats["results_val"] is not None
        assert stats["results_val"][0] is not None
        self.assertEqual(stats["results_val"][0]["n"], 2)
        assert stats["results_val"][1] is not None
        self.assertEqual(stats["results_val"][1]["n"], 2)
        assert plan.procedures[0].calibration is not None
        calibration = plan.procedures[0].calibration.toDict()
        self.assertEqual(len(calibration["calibration_result"][0]),10)
        for i, x in enumerate(calibration["calibration_result"][0]):
            self.assertEqual(x, plan.procedures[0].parameter_list[i])
        self.assertEqual(calibration["calibration_result"][1], stats["results"][0]["oneminusr"])
        self.assertEqual(len(calibration["limits"]),10)

    def test_stats_df(self):
        plan = Plan.load(data_dir / "plans/dummy_sac.yml")
        assert plan.procedures[0].calibration is not None
        plan.procedures[0].calibration.calibrate = False
        plan.execute(upload = False)
        stats_df = plan.procedures[0].read_statistics(as_dataframe=True)
        self.assertTrue(isinstance(stats_df, DataFrame))

    def test_stats_df_score(self):
        plan = Plan.load(data_dir / "plans/dummy_sac.yml")
        plan.execute(upload = False)
        assert plan.procedures[0].calibration is not None
        self.assertTrue(isinstance(plan.procedures[0].calibration.scores, DataFrame))

    def test_calibration_save_result_raise_exception(self):
        plan = Plan.load(data_dir / "plans/dummy_sac.yml")
        assert plan.procedures[0].calibration is not None
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
            list
        )

        assert len(plan.procedures) == 0

        procedure = Procedure(
            1,
            type= "Procedure"
        )
        plan.procedures.append(procedure)

        assert len(plan.procedures) == 1

        for p in plan.procedures:
            assert isinstance(p, Procedure)



    def test_duplicate_procedure(self):
        plan = Plan(
            "plan 0",
            123,
            topology = {
                "timestart": "2000-01-01T12:00:00.000Z",
                "timeend": "2000-01-06T12:00:00.000Z",
                "time_offset": { "hours": 9},
                "nodes": []
            },
            procedures = [
                {
                    "id": 1,
                    "type": "AbstractProcedure",
                    "parameters": [],
                    "boundaries": [],
                    "outputs": []                        
                }
            ]
        )
        self.assertIsInstance(
            plan.procedures,
            list
        )
        for p in plan.procedures:
            assert isinstance(p, Procedure)
        
        procedure = Procedure(
            1,
            type = "AbstractProcedure",
            parameters = [],
            boundaries = [],
            outputs = []
        )
        self.assertRaises(
            DuplicateKeyError,
            plan.procedures.append,
            procedure
        )

    dummy_topology = {
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
    }

    dummy_procedure = {
        "id": "Yacyretá/Pilco - Corrientes",
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

    def test_nan(self):
        plan = Plan(
            name = "test_nan",
            id = 111,
            topology = self.dummy_topology,
            procedures = [
                self.dummy_procedure
            ],
            forecast_date = "2000-01-03T03:00:00.000Z",
            time_interval = {"days": 1}
        )
        self.assertEqual(plan.name,"test_nan")
        self.assertEqual(plan.id, 111)
        self.assertEqual(plan.forecast_date.isoformat(), "2000-01-03T00:00:00-03:00")
        assert plan.topology is not None
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
        plan_config = yaml.load(open(data_dir / "plans/linear_channel_dummy.yml"),yaml.CLoader)
        plan_config["topology"]["save_variable"] = [
            {
                "var_id": 40,
                "output": data_dir / "results/q_data.csv",
                "format": "csv",
                "pivot": True
            }
        ]
        plan = Plan(
            **plan_config
        )
        plan.execute(upload=False)

    def test_batch_process_input_of_procedure(self):
        topology = {**self.dummy_topology}
        topology["nodes"][2]["variables"][0]["series_prono"] = [
            {
                "series_id": 1020,
                "cal_id": 7896,
                "observations": [ 
                    [ "2000-01-04T03:00:00.000Z", 3014.111],
                    [ "2000-01-05T03:00:00.000Z", 3015.111]
                ]
            }
        ]
        plan = Plan(
            name = "test_batch_process_input_of_procedure",
            id = 111,
            topology = self.dummy_topology,
            procedures = [
                self.dummy_procedure
            ],
            forecast_date = "2000-01-03T03:00:00.000Z",
            time_interval = {"days": 1}
        )
        
        plan.procedures[0].batchProcessInput(include_prono=True)

        plan.procedures[0].loadInput()

        assert plan.procedures[0].input is not None
        self.assertEqual(len(plan.procedures[0].input),3)
        self.assertEqual(len(plan.procedures[0].input[0].dropna()),5)
        self.assertEqual(len(plan.procedures[0].input[1].dropna()),5)
        self.assertEqual(len(plan.procedures[0].input[2].dropna()),5)

        plan.procedures[0].loadOutputObs()

        assert plan.procedures[0].output_obs is not None
        self.assertEqual(len(plan.procedures[0].output_obs),1)
        self.assertEqual(len(plan.procedures[0].output_obs[0].dropna()),0)

        plan.procedures[0].run()

        assert plan.procedures[0].output is not None
        self.assertEqual(len(plan.procedures[0].output),1)
        self.assertEqual(len(plan.procedures[0].output[0].dropna()),5)

    def test_raise_duplicate_proc_id(self):
        self.assertRaises(
            DuplicateKeyError, 
            Plan,
            id=9999,
            name="test raise duplicate",
            topology = {
                "timestart": "2022-07-15T03:00:00.000Z",
                "timeend": "2022-07-17T03:00:00.000Z",
                "nodes": [
                    {
                        "id": 1,
                        "name": "andresito",
                        "time_interval": {"days": 1},
                        "variables": [
                            {
                                "id": 2,
                                "series": [
                                    {
                                        "series_id": 8
                                    }
                                ],
                                "series_sim": [
                                    {
                                        "series_id": 3051
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            procedures = [
                {
                    "id": "duplicate",
                    "type": "Polynomial",
                    "parameters": {
                        "intercept": 22.0,
                        "coefficients": [4.0]
                    },
                    "boundaries": [
                        {
                            "name": "input",
                            "node_variable": [1,2]
                        }
                    ],
                    "outputs": [
                        {
                            "name": "output",
                            "node_variable": [1,2]
                        }
                    ]
                },
                {
                    "id": "duplicate",
                    "type": "Polynomial",
                    "parameters": {
                        "intercept": 22.0,
                        "coefficients": [4.0]
                    },
                    "boundaries": [
                        {
                            "name": "input",
                            "node_variable": [1,2]
                        }
                    ],
                    "outputs": [
                        {
                            "name": "output",
                            "node_variable": [1,2]
                        }
                    ]
                }
            ]
        )