from pydrodelta.observed_node_variable import ObservedNodeVariable
from unittest import TestCase

class Test_ObservedNodeVariable(TestCase):

    def test_series_load_api_len(self):
        timestart = "2022-02-18T03:00:00.000Z"
        timeend = "2022-02-22T03:00:00.000Z"
        time_interval = { "hours": 1}
        node_variable = ObservedNodeVariable(
            id = 2,
            series = [
                {
                    "series_id": 38,
                    "tipo": "puntual"
                }
            ],
            series_prono = [
                {
                    "cal_id": 288,
                    "cor_id": 6,
                    "series_id": 3416,
                    "tipo":  "puntual"
                }
            ],
            timestart = timestart,
            timeend = timeend,
            time_interval = time_interval
        )
        node_variable.loadData(
            timestart,
            timeend,
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })   
        self.assertEqual(len(node_variable.series[0].data),3)
        self.assertEqual(len(node_variable.series_prono[0].data),91)

    def test_series_load_api_raise_timestart_not_set(self):
        node_variable = ObservedNodeVariable(
            id = 2,
            series = [
                {
                    "series_id": 38,
                    "tipo": "puntual"
                }
            ],
            series_prono = [
                {
                    "cal_id": 288,
                    "cor_id": 6,
                    "series_id": 3416,
                    "tipo":  "puntual"
                }
            ]
        )
        self.assertRaises(
            Exception,
            node_variable.loadData,
            "2022-02-18T03:00:00.000Z",
            "2022-02-21T03:00:00.000Z",
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })


