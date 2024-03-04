from pydrodelta.topology import Topology
from pydrodelta.node import Node
from pydrodelta.observed_node_variable import ObservedNodeVariable
from pydrodelta.node_serie import NodeSerie
from unittest import TestCase

class Test_Node(TestCase):

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
        