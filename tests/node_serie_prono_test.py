from pydrodelta.node_serie_prono import NodeSerieProno
import unittest
from pandas import DatetimeIndex, DataFrame
from datetime import timedelta

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

    def test_previous_runs_timestart(self):
        node_serie = NodeSerieProno(
            cal_id = 445,
            series_id = 29586,
            tipo = "puntual",
            previous_runs_timestart = {"days": -10},
            qualifier = "main"
        )
        node_serie.loadData(
            {"days": -10},
            {"days": 5},
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            })   
        self.assertTrue(type(node_serie.data),DataFrame)
        self.assertTrue(len(node_serie.data) > 0)
        # self.assertTrue(node_serie.data.dropna().index.min() < node_serie.previous_runs_timestart + timedelta(days=0))
        self.assertTrue(node_serie.data.dropna().index.min() < node_serie.metadata["forecast_date"])
        self.assertTrue(node_serie.metadata["forecast_date"] >= node_serie.previous_runs_timestart)


    def test_series_load_json(self):
        node_serie = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            json_file = "sample_data/json/series_sample.json"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertTrue(isinstance(node_serie.data.index,DatetimeIndex))
        self.assertEqual(node_serie.metadata["series_id"], 1)
        self.assertEqual(node_serie.metadata["series_table"], "series")

    def test_series_load_yaml(self):
        node_serie = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            json_file = "sample_data/yaml/series_sample.yaml"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertTrue(isinstance(node_serie.data.index,DatetimeIndex))
        self.assertEqual(node_serie.metadata["series_id"], 1)
        self.assertEqual(node_serie.metadata["series_table"], "series")

    def test_series_load_csv(self):
        node_serie = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            csv_file = "sample_data/csv/csv_file_sample.csv"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertTrue(isinstance(node_serie.data.index,DatetimeIndex))
        self.assertEqual(node_serie.metadata["series_id"], 1)
        self.assertEqual(node_serie.metadata["series_table"], "series")

    def test_series_save_json(self):
        node_serie = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            json_file = "sample_data/json/series_sample.json"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        output_file = "results/series_prono.json"
        node_serie.saveData(output_file)
        node_serie_2 = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            json_file = output_file
        )
        node_serie_2.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertEqual(len(node_serie.data), len(node_serie_2.data))

    def test_series_save_csv(self):
        node_serie = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            json_file = "sample_data/json/series_sample.json"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        output_file = "results/series_prono.csv"
        node_serie.saveData(output_file, format = "csv")
        node_serie_2 = NodeSerieProno(
            series_id = 1,
            cal_id = 1,
            tipo = "puntual",
            csv_file = output_file
        )
        node_serie_2.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertEqual(len(node_serie.data), len(node_serie_2.data))