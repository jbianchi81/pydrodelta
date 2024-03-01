from pydrodelta.topology import Topology
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
        