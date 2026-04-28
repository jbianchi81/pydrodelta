from pydrodelta.node import Node
from unittest import TestCase
from a5client.util_types import IntervalDict
from typing import List
from pydrodelta.types.abstract_node_serie_dict import AbstractNodeSerieDict
from pydrodelta.types.observed_node_variable_dict import ObservedNodeVariableDict
from pydrodelta.types.node_variable_dict import NodeVariableDict
from pydrodelta.types.node_serie_prono_dict import NodeSeriePronoDict
from dateutil.relativedelta import relativedelta

class Test_Node(TestCase):

    def test_node_load_api_len(self):
        timestart : IntervalDict = {"days": -3}
        timeend : IntervalDict = {"days": 30}
        time_interval : IntervalDict = { "days": 1}
        s : List[AbstractNodeSerieDict] = [
                        {
                            "series_id": 26282,
                            "tipo": "puntual"
                        },
                        {
                            "series_id": 41,
                            "tipo": "puntual"
                        }
                    ] 
        sp : List[NodeSeriePronoDict] = [
                        {
                            "cal_id": 499,
                            "series_id": 35471,
                            "tipo":  "puntual"
                        }
                    ]
        v : NodeVariableDict = {
            "id": 39,
            "series": s,
            "series_prono": sp
        }
        node = Node(
            id = 1,
            name = "node 1",
            timestart = timestart,
            timeend = timeend,
            time_interval = time_interval,
            variables = [ v ]
        )
        node.loadData(
            timestart,
            timeend,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            }) 
        series = node.variables[39].series
        assert series is not None  
        assert len(series)
        assert series[0].data is not None  
        assert len(series[0].data) >= 2
        assert len(series[0].data) >= 2
        series_prono = node.variables[39].series_prono
        assert series_prono is not None
        assert len(series_prono[0].data) >= 4

    def test_area_retrieve_metadata(self):
        timestart = "2022-02-18T03:00:00.000Z"
        timeend = "2022-02-22T03:00:00.000Z"
        time_interval = relativedelta(hours=1)
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
        assert node.basin_pars is not None
        self.assertTrue("area" in node.basin_pars)        
        self.assertIsNotNone(node.basin_pars["area"])
        self.assertAlmostEqual(node.basin_pars["area"],45250735227.4144,1)