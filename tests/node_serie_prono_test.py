from pydrodelta.node_serie_prono import NodeSerieProno
import unittest

class Test_NodeSerieProno(unittest.TestCase):

    def test_series_load_api_len(self):
        node_serie = NodeSerieProno(
            cal_id = 5,
            series_id = 64006,
            tipo = "puntual"
        )
        node_serie.loadData(
            "2023-04-01T00:00:00.000Z",
            "2023-08-01T00:00:00.000Z",
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })   
        self.assertEqual(len(node_serie.data),4)
