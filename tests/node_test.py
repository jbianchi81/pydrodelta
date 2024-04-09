from pydrodelta.node import Node
from unittest import TestCase

class Test_Node(TestCase):

    def test_node_load_api_len(self):
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
        )
        node.loadData(
            timestart,
            timeend,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })   
        self.assertEqual(len(node.variables[2].series[0].data),3)
        self.assertEqual(len(node.variables[2].series_prono[0].data),91)

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
                "area_id": 614
            },
            api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            }
        )
        self.assertIsNotNone(node.basin_pars)
        self.assert_("area" in node.basin_pars)        
        self.assertIsNotNone(node.basin_pars["area"])
        self.assertEqual(node.basin_pars["area"],140273473.449287)
