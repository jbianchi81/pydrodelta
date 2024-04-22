from pydrodelta.node_serie import NodeSerie
import unittest
from pandas import DataFrame, DatetimeIndex

class Test_NodeSerie(unittest.TestCase):
    
    def test_series_id(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            observations = []
        )
        self.assertEqual(node_serie.series_id,1)
    
    def test_series_load_inline_data(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["2000-01-01T03:00:00.000Z", 1.01],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )
        node_serie.loadData("2000-01-01T03:00:00.000Z","2000-01-03T03:00:00.000Z")   
        self.assert_(isinstance(node_serie.data,DataFrame))
        
    def test_series_load_inline_data_len(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["2000-01-01T03:00:00.000Z", 1.01],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )
        node_serie.loadData("2000-01-01T03:00:00.000Z","2000-01-03T03:00:00.000Z")   
        self.assertEqual(len(node_serie.data),2)

    def test_series_load_inline_data_index_type(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["2000-01-01T03:00:00.000Z", 1.01],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )
        node_serie.loadData("2000-01-01T03:00:00.000Z","2000-01-03T03:00:00.000Z")   
        self.assert_(isinstance(node_serie.data.index,DatetimeIndex))

    def test_series_load_inline_data_outside_range(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["2000-01-01T03:00:00.000Z", 1.01],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )
        node_serie.loadData("2000-01-03T03:00:00.000Z","2000-01-05T03:00:00.000Z")   
        self.assertEqual(len(node_serie.data),0)

    def test_series_load_inline_data_partially_in_range(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["2000-01-01T03:00:00.000Z", 1.01],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )
        node_serie.loadData("2000-01-02T03:00:00.000Z","2000-01-05T03:00:00.000Z")   
        self.assertEqual(len(node_serie.data),1)

    def test_series_load_csv_len(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            csv_file = "sample_data/csv/csv_file_sample.csv"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")   
        self.assertEqual(len(node_serie.data),24)

    def test_series_load_api_len(self):
        node_serie = NodeSerie(
            series_id = 8,
            tipo = "puntual"
        )
        node_serie.loadData(
            "2022-07-15T03:00:00.000Z",
            "2022-07-18T03:00:00.000Z",
            input_api_config = {
                "url": "https://alerta.ina.gob.ar/test",
                "token": "MY_TOKEN"
            })   
        self.assertEqual(len(node_serie.data),3)

    def test_series_bad_id(self):
        self.assertRaises(
            ValueError,
            NodeSerie,
            series_id = "a"
        )

    def test_series_bad_date(self):
        self.assertRaises(
            ValueError,
            NodeSerie,
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["200a0-01-01T03:00:00.000Z", 1.01],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )

    def test_series_bad_value(self):
        self.assertRaises(
            ValueError,
            NodeSerie,
            series_id = 1,
            tipo = "puntual",
            observations = [
                ["2000-01-01T03:00:00.000Z", "a1.01"],
                ["2000-01-02T03:00:00.000Z", 2.02],
            ]
        )

    def test_series_load_json(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            json_file = "sample_data/json/series_sample.json"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assert_(isinstance(node_serie.data.index,DatetimeIndex))

    def test_series_load_yaml(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            json_file = "sample_data/yaml/series_sample.yaml"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assert_(isinstance(node_serie.data.index,DatetimeIndex))

    def test_series_save_json(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            csv_file = "sample_data/csv/csv_file_sample.csv"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        output_file = "results/series_sample.json"
        node_serie.saveData(output_file)
        node_serie_2 = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            json_file = "results/series_sample.json"
        )
        node_serie_2.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertEqual(len(node_serie.data), len(node_serie_2.data))

    def test_series_save_yaml(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            csv_file = "sample_data/csv/csv_file_sample.csv"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        output_file = "results/series_sample.yaml"
        node_serie.saveData(output_file, format="yaml")
        node_serie_2 = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            json_file = "results/series_sample.yaml"
        )
        node_serie_2.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertEqual(len(node_serie.data), len(node_serie_2.data))

    def test_series_save_json_list(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            csv_file = "sample_data/csv/csv_file_sample.csv"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        output_file = "results/series_sample_list.json"
        node_serie.saveData(output_file, schema = "list")
        node_serie_2 = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            json_file = "results/series_sample_list.json"
        )
        node_serie_2.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertEqual(len(node_serie.data), len(node_serie_2.data))

    def test_series_save_csv(self):
        node_serie = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            csv_file = "sample_data/csv/csv_file_sample.csv"
        )
        node_serie.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        output_file = "results/series_sample.csv"
        node_serie.saveData(output_file,format = "csv")
        node_serie_2 = NodeSerie(
            series_id = 1,
            tipo = "puntual",
            csv_file = "results/series_sample.csv"
        )
        node_serie_2.loadData("2023-04-23T03:00:00.000Z","2023-04-24T02:00:00.000Z")
        self.assertEqual(len(node_serie.data), len(node_serie_2.data))

if __name__ == '__main__':
    unittest.main()