from pydrodelta.observed_node_variable import ObservedNodeVariable
from unittest import TestCase
from datetime import timedelta
from pydrodelta.types.typed_list import TypedList
from pydrodelta.node_serie import NodeSerie
from pydrodelta.node_serie_prono import NodeSerieProno

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

    def test_series_prono_concat(self):
        timestart = {"days": -20}
        timeend = {"days": 5}
        time_interval = { "hours": 1}
        node_variable = ObservedNodeVariable(
            id = 2,
            series = [
                {
                    "series_id": 52,
                    "tipo": "puntual"
                }
            ],
            series_prono = [
                {
                    "cal_id": 445,
                    "series_id": 29586,
                    "tipo":  "puntual",
                    "qualifier": "main",
                    "previous_runs_timestart": {"days": -10}
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
                "url": "https://alerta.ina.gob.ar/a5",
                "token": "MY_TOKEN"
            })   
        self.assertTrue(len(node_variable.series[0].data)>0)
        self.assertTrue(len(node_variable.series_prono[0].data)>0)
        self.assertTrue(node_variable.series_prono[0].data.dropna().index.min() < node_variable.series_prono[0].previous_runs_timestart + timedelta(days=0))

    def test_append_serie(self):
        variable = ObservedNodeVariable(
            id = 20
        )
        self.assertIsNone(variable.series)
        variable.series = [
            1,
            {
                "series_id": 2
            },
            NodeSerie(3)
        ]
        
        self.assertEqual(len(variable.series),3)
        self.assertEqual(type(variable.series),TypedList)
        variable.series.append([4])
        self.assertEqual(len(variable.series),4)
        variable.series.extend([5,6])
        self.assertEqual(len(variable.series),6)
        for i, s in enumerate(variable.series):
            self.assertEqual(type(s), NodeSerie)
            self.assertEqual(s.series_id, i + 1)
    

    def test_get_serie(self):
        variable = ObservedNodeVariable(
            id = 20
        )
        variable.series = [
            1,
            2,
            3
        ]
        serie = variable.getSerie(1)
        self.assertEqual(type(serie), NodeSerie)
        self.assertEqual(serie.series_id,1)

    def test_assert_get_serie(self):
        variable = ObservedNodeVariable(
            id = 20
        )
        self.assertIsNone(variable.series)
        variable.series = [
            1,
            2,
            3
        ]
        self.assertRaises(KeyError, variable.getSerie, 4)

    def test_get_serie_prono(self):
        variable = ObservedNodeVariable(
            id = 20,
            series = [1, 2, 3],
            series_prono = [
                {
                    "series_id": 4,
                    "cal_id": 1234
                }
            ]
        )
        serie = variable.getSerie(4,"series_prono")
        self.assertEqual(type(serie), NodeSerieProno)
        self.assertEqual(serie.series_id,4)

    def test_get_serie_prono_assert_no_cal_id(self):
        variable = ObservedNodeVariable(id = 20, series_prono = [])
        self.assertRaises(TypeError,variable.series_prono.append,{"series_id": 4})

    def test_get_serie_sim(self):
        variable = ObservedNodeVariable(
            id = 20,
            series_sim = [
                {
                    "series_id": 4
                }
            ]
        )
        serie = variable.getSerie(4,"series_sim")
        self.assertEqual(type(serie), NodeSerieProno)
        self.assertEqual(serie.series_id,4)

    def test_get_serie_output(self):
        variable = ObservedNodeVariable(
            id = 20,
            series_output = [
                {
                    "series_id": 4
                }
            ]
        )
        serie = variable.getSerie(4,"series_output")
        self.assertEqual(type(serie), NodeSerie)
        self.assertEqual(serie.series_id,4)

    def test_pop_serie(self):
        variable = ObservedNodeVariable(
            id = 20
        )
        variable.series = [
            1,
            2,
            3
        ]
        self.assertEqual(len(variable.series),3)
        serie = variable.series.pop()
        self.assertEqual(len(variable.series),2)
        self.assertEqual(type(serie), NodeSerie)

    def test_serie_variable_property(self):
        variable = ObservedNodeVariable(
            id = 20,
            series = [1]
        )
        self.assertIsNotNone(variable.getSerie(1)._variable)
        self.assertEqual(type(variable.getSerie(1)._variable), ObservedNodeVariable)
        self.assertEqual(variable.getSerie(1)._variable, variable)
        variable.series.append(2)
        self.assertEqual(variable.getSerie(2)._variable, variable)
        variable.series.append({"series_id":3})
        self.assertEqual(variable.getSerie(3)._variable, variable)
        variable.series.append((4))
        self.assertEqual(variable.getSerie(4)._variable, variable)

    def test_duplicate_serie_id(self):
        variable = ObservedNodeVariable(
            id = 20,
            series = [1]
        )
        self.assertRaises(
            ValueError,
            variable.series.append,
            1
        )
