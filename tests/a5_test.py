from pydrodelta.a5 import Observacion, Serie, Crud, observacionesListToDataFrame, observacionesDataFrameToList, createEmptyObsDataFrame
import unittest
from pydrodelta.util import tryParseAndLocalizeDate
from pandas import DataFrame, DatetimeIndex
from datetime import timedelta

class Test_a5Observacion(unittest.TestCase):
    
    def test_constructor(self):
        observacion = Observacion(
            timestart = "2020-01-01T03:00:00.000Z",
            valor = 123.456,
            tipo = "puntual",
        )
        self.assertEqual(observacion.timestart.isoformat(),"2020-01-01T00:00:00-03:00")
        self.assertEqual(observacion.tipo,"puntual")
        self.assertEqual(observacion.valor,123.456)

    def test_to_dict(self):
        observacion_dict = Observacion(
            timestart = "2020-01-01T03:00:00.000Z",
            valor = 123.456,
            tipo = "puntual"
        ).toDict()        
        self.assertEqual(observacion_dict["timestart"],"2020-01-01T00:00:00-03:00")
        self.assertEqual(observacion_dict["valor"],123.456)
        self.assertEqual(observacion_dict["tipo"],"puntual")

class Test_a5Serie(unittest.TestCase):
    
    def test_constructor(self):
        serie = Serie(
            id = 1345,
            tipo = "puntual",
            observaciones = [
                {
                    "timestart": "2020-01-01T03:00:00.000Z",
                    "valor": 123.456,
                    "tipo": "puntual"
                }
            ]
        )
        self.assertEqual(serie.id, 1345)
        self.assertEqual(serie.tipo, "puntual")
        self.assertEqual(len(serie.observaciones), 1)
        self.assertEqual(serie.observaciones[0].timestart.isoformat(),"2020-01-01T00:00:00-03:00")
        self.assertEqual(serie.observaciones[0].tipo,"puntual")
        self.assertEqual(serie.observaciones[0].valor,123.456)

    def test_to_dict(self):
        serie_dict = Serie(
            id = 1345,
            tipo = "puntual",
            observaciones = [
                {
                    "timestart": "2020-01-01T03:00:00.000Z",
                    "valor": 123.456,
                    "tipo": "puntual"
                }
            ]
        ).toDict()
        self.assertEqual(serie_dict["id"], 1345)
        self.assertEqual(serie_dict["tipo"], "puntual")
        self.assertEqual(len(serie_dict["observaciones"]), 1)
        self.assertEqual(serie_dict["observaciones"][0]["timestart"],"2020-01-01T00:00:00-03:00")
        self.assertEqual(serie_dict["observaciones"][0]["valor"],123.456)
        self.assertEqual(serie_dict["observaciones"][0]["tipo"],"puntual")

class Test_a5Crud(unittest.TestCase):
    
    def test_constructor(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/test",
            token = "my_token"
        )
        self.assertEqual(crud.url, "https://alerta.ina.gob.ar/test")
        self.assertEqual(crud.token, "my_token")
        self.assertIsNone(crud.proxy_dict)
    
    def test_read_series(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/test",
            token = "my_token"
        )
        data = crud.readSeries(include_geom=False, no_metadata=True, var_id=2, proc_id=1)
        self.assert_("rows" in data)
        self.assertEqual(type(data["rows"]), list)
        self.assert_(len(data) > 0)
        for row in data["rows"]:
            self.assertEqual(row["var_id"],2)
            self.assertEqual(row["proc_id"],1)

    def test_read_serie(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/test",
            token = "my_token"
        )
        series_id = 8
        timestart = tryParseAndLocalizeDate("2022-07-15T03:00:00.000Z")
        timeend = tryParseAndLocalizeDate("2022-07-17T03:00:00.000Z")
        data = crud.readSerie(
            series_id,
            timestart = timestart,
            timeend = timeend,
            tipo = "puntual"
        )
        self.assert_("observaciones" in data)
        self.assertEqual(type(data["observaciones"]), list)
        self.assert_(len(data["observaciones"]) > 0)
        for row in data["observaciones"]:
            self.assertEqual(row["series_id"],series_id)
            self.assert_(tryParseAndLocalizeDate(row["timestart"]) >= timestart)
            self.assert_(tryParseAndLocalizeDate(row["timestart"]) <= timeend)
            self.assertEqual(type(row["valor"]),float)
    
    def test_read_calibrado(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/test",
            token = "my_token"
        )
        cal_id = 288
        data = crud.readCalibrado(cal_id)
        self.assertEqual(type(data),dict)
        self.assert_("id" in data)
        self.assertEqual(data["id"],cal_id)

    def test_read_var(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/a5",
            token = "my_token"
        )
        data = crud.readVar(2)
        self.assertEqual(type(data),dict)
        self.assert_("id" in data)
        self.assertEqual(data["id"],2)

    def test_read_serie_prono(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/a5",
            token = "my_token"
        )
        data = crud.readSerieProno(
            1540,
            289
        )
        self.assertEqual(type(data),dict)
        self.assertEqual(data["cal_id"],289)
        self.assertEqual(data["series_id"],1540)
        self.assert_("pronosticos" in data)
        self.assertEqual(type(data["pronosticos"]), list)
        self.assert_(len(data["pronosticos"]) > 0)
        for x in data["pronosticos"]:
            self.assert_("timestart" in x)
            self.assert_("valor" in x)

    def test_list_to_dataframe(self):
        df = observacionesListToDataFrame(
            [
                {
                    "timestart": "2000-01-01T03:00:00.000Z", 
                    "valor": 1.01
                },
                {
                    "timestart": "2000-01-02T03:00:00.000Z", 
                    "valor": 2.02
                }
            ], 
            tag = "observed"
        )
        self.assertEqual(type(df), DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(len(df.columns), 2)
        self.assert_("valor" in df.columns)
        self.assert_("tag" in df.columns)
        self.assertEqual(type(df.index), DatetimeIndex)

    def test_dataframe_to_list(self):
        df = DataFrame([
            {
                "timestart": tryParseAndLocalizeDate("2000-01-01T03:00:00.000Z"), 
                "valor": 1.01
            },
            {
                "timestart": tryParseAndLocalizeDate("2000-01-02T03:00:00.000Z"), 
                "valor": 2.02
            }
        ])
        df = df.set_index("timestart")
        data = observacionesDataFrameToList(
            df,
            1,
            column = "valor",
            timeSupport = timedelta(days=1)
        )
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 2)
        for x in data:
            self.assertEqual((tryParseAndLocalizeDate(x["timeend"]) - tryParseAndLocalizeDate(x["timestart"])).days,1)

    def test_empty_dataframe(self):
        df = createEmptyObsDataFrame(
            extra_columns = {"tag": str}
        )
        self.assertEqual(type(df), DataFrame)
        self.assertEqual(len(df), 0)
        self.assertEqual(len(df.columns), 2)
        self.assert_("valor" in df.columns)
        self.assert_("tag" in df.columns)
        self.assertEqual(type(df.index), DatetimeIndex)

    def test_read_corridas(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/a5",
            token = "my_token"
        )
        data = crud.readCorridas(
            289
        )
        self.assertEqual(type(data),list)
        for corrida in data:
            self.assertEqual(corrida["cal_id"],289)
            self.assert_("id" in corrida)
            self.assert_("series" in corrida)
            self.assertEqual(type(corrida["series"]), list)
            self.assert_(len(corrida["series"]) > 0)
            for serie in corrida["series"]:
                self.assert_("series_id" in serie)
                self.assert_("pronosticos" in serie)
                self.assertEqual(type(serie["pronosticos"]), list)
            
    def test_read_serie_prono_concat(self):
        crud = Crud(
            url = "https://alerta.ina.gob.ar/a5",
            token = "my_token"
        )
        serie = crud.readSeriePronoConcat(
            445,
            29586,
            qualifier = "main"
        )
        self.assertEqual(type(serie),dict)
        self.assertEqual(serie["series_id"],29586)
        self.assert_("pronosticos" in serie)
        self.assertEqual(type(serie["pronosticos"]),list)
        self.assert_(len(serie["pronosticos"]) > 0)
        ts = [p["timestart"] for p in serie["pronosticos"]]
        self.assertEqual(len(ts),len(set(ts)))
        for pronostico in serie["pronosticos"]:
            self.assertEqual(type(pronostico),dict)
            self.assert_("timestart" in pronostico)
            self.assert_("valor" in pronostico)
            self.assert_("cor_id" in pronostico)
            self.assertEqual(pronostico["qualifier"],"main")