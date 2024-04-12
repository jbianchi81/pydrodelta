from pydrodelta.topology import Topology
from pydrodelta.node import Node
from pydrodelta.observed_node_variable import ObservedNodeVariable
from pydrodelta.node_serie import NodeSerie
from unittest import TestCase
import os
import yaml
import time

class Test_Topology(TestCase):

    def test_topology_load_api_len(self):
        timestart = "2022-02-18T03:00:00.000Z"
        timeend = "2022-02-22T02:00:00.000Z"
        time_interval = { "hours": 1}
        topology = Topology(
            timestart = timestart,
            timeend = timeend,                    
            nodes = [
                {
                    "id": 1,
                    "name": "node 1",
                    "time_interval": time_interval,
                    "variables": [
                        {
                            "id": 2,
                            "series": [
                                {
                                    "series_id": 38,
                                    "tipo": "puntual"
                                }
                            ],
                            "series_prono": [
                                {
                                    "cal_id": 288,
                                    "cor_id": 6,
                                    "series_id": 3416,
                                    "tipo":  "puntual"
                                }
                            ]
                        }
                    ]
                }
            ]
        )
        topology.loadData(
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })   
        self.assertEqual(len(topology.nodes[0].variables[2].series[0].data),3)
        self.assertEqual(len(topology.nodes[0].variables[2].series_prono[0].data),91)
        
    def test_topology_batch(self):
        timestart = "2022-02-18T03:00:00.000Z"
        timeend = "2022-02-22T02:00:00.000Z"
        time_interval = { "hours": 1}
        topology = Topology(
            timestart = timestart,
            timeend = timeend,                    
            nodes = [
                {
                    "id": 1,
                    "name": "node 1",
                    "time_interval": time_interval,
                    "variables": [
                        {
                            "id": 2,
                            "series": [
                                {
                                    "series_id": 38,
                                    "tipo": "puntual"
                                }
                            ],
                            "series_prono": [
                                {
                                    "cal_id": 288,
                                    "cor_id": 6,
                                    "series_id": 3416,
                                    "tipo":  "puntual"
                                }
                            ]
                        }
                    ]
                }
            ]
        )
        topology.batchProcessInput(
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })
        self.assertEqual(len(topology.nodes[0].variables[2].data),95)
    
    def test_no_metadata(self):
        topology = Topology(
            timestart = "2024-03-03T12:00:00.000Z",
            timeend = "2024-03-07T12:00:00.000Z",
            interpolation_limit =  {"hours": 12},
            no_metadata = True,
            nodes = [
              {
                "id": 1,
                "name": "pma",
                "time_interval": {"days": 1},
                "variables": [
                  {
                    "id": 1,
                    "series": [
                      {
                        "series_id": 6505,
                        "tipo": "areal",
                        "comment": "dummy areal"
                      }
                    ]
                  }
                ]
              }
            ]
        )
        topology.loadData(input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })
        self.assert_(topology.no_metadata)
        self.assertIsInstance(topology.nodes,list)
        self.assertEqual(len(topology.nodes),1)
        self.assertIsInstance(topology.nodes[0],Node)
        self.assertIsInstance(topology.nodes[0].variables,dict)
        self.assertIn(1,topology.nodes[0].variables)
        self.assertIsInstance(topology.nodes[0].variables[1],ObservedNodeVariable)
        self.assertIsInstance(topology.nodes[0].variables[1].series,list)
        self.assertEqual(len(topology.nodes[0].variables[1].series),1)
        self.assertIsInstance(topology.nodes[0].variables[1].series[0],NodeSerie)
        self.assertIn("estacion",topology.nodes[0].variables[1].series[0].metadata)
        self.assertNotIn("geom",topology.nodes[0].variables[1].series[0].metadata["estacion"])

    def test_variable_plot(self):
        topology = Topology(
            timestart = "2024-03-03T12:00:00.000Z",
            timeend = "2024-03-07T12:00:00.000Z",
            forecast_timeend = "2024-03-11T12:00:00.000Z",
            interpolation_limit =  {"hours": 12},
            no_metadata = True,
            nodes = [
              {
                "id": 1,
                "name": "h",
                "time_interval": {"days": 1},
                "variables": [
                  {
                    "id": 4,
                    "series": [
                      {
                        "series_id": 1,
                        "tipo": "puntual",
                        "comment": "dummy puntual",
                        "observations": [
                            ["2024-03-03T12:00:00.000Z", 0.1],
                            ["2024-03-04T12:00:00.000Z", 0.4],
                            ["2024-03-05T12:00:00.000Z", 0.3],
                            ["2024-03-06T12:00:00.000Z", 0.8],
                            ["2024-03-07T12:00:00.000Z", 1.1]
                        ]
                      }
                    ],
                    "series_prono":  [
                        {
                            "series_id": 1,
                            "tipo": "puntual",
                            "comment": "dummy prono",
                            "observations": [
                                ["2024-03-06T12:00:00.000Z", 0.82],
                                ["2024-03-07T12:00:00.000Z", 1.12],
                                ["2024-03-08T12:00:00.000Z", 1.3],
                                ["2024-03-09T12:00:00.000Z", 1.8],
                                ["2024-03-10T12:00:00.000Z", 1.4]
                            ],
                            "cal_id": 1
                        }
                    ]
                  }
                ]
              }
            ]
        )
        topology.batchProcessInput(include_prono=True)
        topology.nodes[0].variables[4].plot()
        topology.plotVariable(
            var_id = 4,
            output = "%s/results/h_plot.pdf" % os.environ["PYDRODELTA_DIR"]
        )
    
    def test_plot_prono(self):
        config = yaml.load(open("%s/sample_data/topologies/plot_prono_dummy.yml" % os.environ["PYDRODELTA_DIR"]),yaml.CLoader)
        topology = Topology(**config)
        topology.batchProcessInput(include_prono=False)
        self.assertIsNotNone(topology.nodes[0].variables[39].series_prono[0].plot_params)
        self.assert_("output_file" in topology.nodes[0].variables[39].series_prono[0].plot_params)
        file_mtime = os.path.getmtime("%s/%s" % (os.environ["PYDRODELTA_DIR"], topology.nodes[0].variables[39].series_prono[0].plot_params["output_file"]))
        self.assert_(file_mtime  > time.time() - 10)
