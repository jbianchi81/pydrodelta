from pydrodelta.node import Node
from unittest import TestCase
from a5client.util_types import IntervalDict

class Test_Node(TestCase):

    def test_node_load_api_len(self):
        timestart : IntervalDict = {"days": -3}
        timeend : IntervalDict = {"days": 30}
        time_interval : IntervalDict = { "days": 1}
        node = Node(
            id = 1,
            name = "node 1",
            timestart = timestart,
            timeend = timeend,
            time_interval = time_interval,
            variables = [
                {
                    "id": 39,
                    "series": [
                        {
                            "series_id": 26282,
                            "tipo": "puntual"
                        },
                        {
                            "series_id": 41,
                            "tipo": "puntual"
                        }
                    ],
                    "series_prono": [
                        {
                            "cal_id": 499,
                            "series_id": 35471,
                            "tipo":  "puntual"
                        }
                    ]
                }
            ]
        )
        node.loadData(
            timestart,
            timeend,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            })   
        assert len(node.variables[39].series[0].data) >= 2
        assert len(node.variables[39].series[1].data) >= 2
        assert len(node.variables[39].series_prono[0].data) >= 4

    def test_area_retrieve_metadata(self):
        timestart = "2022-02-18T03:00:00.000Z"
        timeend = "2022-02-22T03:00:00.000Z"
        time_interval = { "hours": 1}
        node = Node(
            id = 1,
            name = "node 1",
            timestart = timestart,
            timeend = timeend,
            time_interval = time_interval,
            variables = [
                {
                    "id": 1,
                    "series": [
                        {
                            "series_id": 1,
                            "tipo": "areal"
                        }
                    ]
                }
            ],
            node_type = "basin",
            basin_pars = {
                "area_id": 365
            },
            api_config = {
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            }
        )
        self.assertIsNotNone(node.basin_pars)
        self.assertTrue("area" in node.basin_pars)        
        self.assertIsNotNone(node.basin_pars["area"])
        self.assertAlmostEqual(node.basin_pars["area"],45250735227.4144,1)