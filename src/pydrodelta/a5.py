from jsonschema import validate as json_validate
import requests
import pandas
import pydrodelta.util as util
import json
import os
from datetime import datetime, timedelta
import yaml
import logging
from pydrodelta.config import config
from typing import List, Union
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .descriptors.datetime_descriptor import DatetimeDescriptor
from .descriptors.float_descriptor import FloatDescriptor
from .descriptors.dict_descriptor import DictDescriptor
logging.basicConfig(filename="%s/%s" % (os.environ["PYDRODELTA_DIR"],config["log"]["filename"]), level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
logging.FileHandler("%s/%s" % (os.environ["PYDRODELTA_DIR"],config["log"]["filename"]),"w+")

from .a5_schemas import schemas

serie_schema = open("%s/data/schemas/yaml/serie.yml" % os.environ["PYDRODELTA_DIR"])
serie_schema = yaml.load(serie_schema,yaml.CLoader)

def validate(
    instance : dict,
    classname : str
    ) -> None:
    """_summary_

    Args:
        instance (dict): An instance of the class to validate
        classname (str): the name of the class to validate against

    Raises:
        Exception: Invalid class if classname is not in schemas

        ValidationError: If instance does not validate against schema
    """
    if classname not in schemas["components"]["schemas"].keys():
        raise Exception("Invalid class")
    return json_validate(instance,schema=schemas) #[classname])

# CLASSES

class Observacion():
    """Represents a time-value pair of an observed variable"""

    timestart = DatetimeDescriptor() # util.tryParseAndLocalizeDate(params["timestart"])
    """begin timestamp of the observation"""

    valor = FloatDescriptor()
    """value of the observation"""
    
    timeend = DatetimeDescriptor() # (None, False) if "timeend" not in params else util.tryParseAndLocalizeDate(params["timeend"])
    """end timestamp of the observation"""

    series_id = IntDescriptor()
    """Series identifier"""

    tipo = StringDescriptor()
    """Series geometry type (puntual, areal, raster)"""

    tag = StringDescriptor()
    """Observation tag"""

    def __init__(
        self,
        timestart : datetime,
        valor : float,
        timeend : datetime = None,
        series_id : int = None,
        tipo : str = "puntual",
        tag : str = None
    ):
        """
        Args:
            timestart (datetime): begin timestamp of the observation
            valor (float): value of the observation
            timeend (datetime, optional): end timestamp of the observation. Defaults to None.
            series_id (int, optional): Series identifier. Defaults to None.
            tipo (str, optional): Series geometry type (puntual, areal, raster) . Defaults to "puntual".
            tag (str, optional): Observation tag. Defaults to None.
        """
        # json_validate(params,"Observacion")
        self.timestart = timestart
        self.timeend = timeend
        self.valor = valor
        self.series_id = series_id
        self.tipo = tipo
        self.tag = tag

    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "timestart": self.timestart.isoformat(),
            "timeend": self.timeend.isoformat() if self.timeend is not None else None,
            "valor": self.valor,
            "series_id": self.series_id,
            "tipo": self.tipo,
            "tag": self.tag
        }

class Serie():
    """Represents a timeseries of a variable in a site, obtained through a method, and measured in a units"""

    id = IntDescriptor()
    """Identifier"""

    tipo = StringDescriptor()
    """Geometry type: puntual, areal, raster"""

    @property
    def observaciones(self) -> List[Observacion]:
        """Observations"""
        return self._observaciones
    @observaciones.setter
    def observaciones(
        self,
        observaciones : List[dict] = []
    ) -> None:
        self._observaciones = [o if isinstance(o,Observacion) else Observacion(**o) for o in observaciones]

    def __init__(
        self,
        id : int = None,
        tipo : str = None,
        observaciones : List[dict] = []
        ):
        """
        Args:
            id (int, optional): Identifier. Defaults to None.
            tipo (str, optional): Geometry type: puntual, areal, raster. Defaults to None.
            observaciones (List[dict], optional): Observations. Each dict must have timestart (datetime) and valor (float). Defaults to [].
        """
        json_validate({"id": id, "tipo": tipo, "observaciones": observaciones}, schema=serie_schema)
        self.id = id
        self.tipo = tipo
        self.observaciones = observaciones
    def toDict(self) -> dict:
        """Convert to dict"""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "observaciones": [o.toDict() for o in self.observaciones]
        }
            
# CRUD

class Crud():
    """a5 api client"""

    url = StringDescriptor()
    """api url"""

    token = StringDescriptor()
    """ api authorization token"""

    proxy_dict = DictDescriptor()
    """proxy parameters"""

    def __init__(
        self,
        url : str,
        token : str,
        proxy_dict : dict = None
        ):
        """
        Args:
            url (str): api url
            token (str): api authorization token
            proxy_dict (dict, optional): proxy parameters. Defaults to None.
        """
        self.url = url
        self.token = token
        self.proxy_dict = proxy_dict
    
    def readSeries(
        self,
        tipo : str = "puntual",
        series_id : int = None,
        area_id : int = None,
        estacion_id : int = None,
        escena_id : int = None,
        var_id : int = None,
        proc_id : int = None,
        unit_id : int = None,
        fuentes_id : int = None,
        tabla : str = None,
        id_externo : str = None,
        geom : Union[str,dict] = None,
        include_geom : bool = None,
        no_metadata : bool = None,
        date_range_before : datetime = None,
        date_range_after : datetime = None,
        getMonthlyStats : bool = None,
        getStats : bool = None,
        getPercentiles : bool = None,
        percentil : float = None,
        use_proxy : bool = False
        ) -> dict:
        """Retrieve series

        Args:
            tipo (str, optional): series type: puntual, areal, raster. Defaults to "puntual".
            series_id (int, optional): Series identifier. Defaults to None.
            area_id (int, optional): Area identifier (with tipo=areal). Defaults to None.
            estacion_id (int, optional): Estacion identifier (with tipo=puntual). Defaults to None.
            escena_id (int, optional): Escena identifier (with tipo=raster). Defaults to None.
            var_id (int, optional): Variable identifier. Defaults to None.
            proc_id (int, optional): Procedure identifier. Defaults to None.
            unit_id (int, optional): Unit identifier. Defaults to None.
            fuentes_id (int, optional): Fuente (source) identifier (with tipo=areal or tipo=raster). Defaults to None.
            tabla (str, optional): Network identifier (with tipo="puntual"). Defaults to None.
            id_externo (str, optional): External station identifier (with tipo=puntual). Defaults to None.
            geom (Union[str,dict], optional): Bounding box. Defaults to None.
            include_geom (bool, optional): Include geometry in response. Defaults to None.
            no_metadata (bool, optional): Exclude metadata from response. Defaults to None.
            date_range_before (datetime, optional): Only retrieve series starting before this date. Defaults to None.
            date_range_after (datetime, optional): Only retrieve series ending after this date. Defaults to None.
            getMonthlyStats (bool, optional): retrieve monthly statistics. Defaults to None.
            getStats (bool, optional): Retrieve statistics. Defaults to None.
            getPercentiles (bool, optional): Retrieve percentiles. Defaults to None.
            percentil (float, optional): Percentile [0-1]. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            data : dict. Api response. Retrieved series list is in data["rows"]
        """
        if date_range_before is not None:
            date_range_before = date_range_before if isinstance(date_range_before,str) else date_range_before.isoformat()
        if date_range_after is not None:
            date_range_after =date_range_after if isinstance(date_range_after,str) else date_range_after.isoformat()
        params = locals()
        del params["use_proxy"]
        del params["tipo"]
        response = requests.get("%s/obs/%s/series" % (self.url, tipo),
            params = params,
            headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readArea(
        self,
        area_id : int,
        use_proxy : bool = False,
        no_geom : bool = False
    ) -> dict:
        """
        Retrieve area
        
        Args:
            area_id : int - area identifier
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.
            no_metadata (bool, optional): Don't retrieve geometry. Defaults to False
                
        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: raw area dict
        """
        params = {
            "no_geom": no_geom
        }
        response = requests.get("%s/obs/areal/areas/%i" % (self.url, area_id),
            params = params,
            headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed for area id: %s. message: %s" % (area_id, response.text))
        json_response = response.json()
        return json_response

    def readSerie(
        self,
        series_id : int,
        timestart : datetime = None,
        timeend : datetime = None,
        tipo : str = "puntual",
        use_proxy : bool = False,
        no_metadata : bool = False
        ) -> dict:
        """Retrieve serie

        Args:
            series_id (int): Series identifier
            timestart (datetime, optional): Begin timestamp. Defaults to None.
            timeend (datetime, optional): End timestamp. Defaults to None.
            tipo (str, optional): Geometry type: puntual, areal, raster. Defaults to "puntual".
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.
            no_metadata (bool, optional): Don't retrieve metadata (only data and identifiers). Defaults to False

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: raw serie dict
        """
        params = {
            "no_metadata": no_metadata
        }
        if timestart is not None and timeend is not None:
            params["timestart"] = timestart if isinstance(timestart,str) else timestart.isoformat()
            params["timeend"] = timeend if isinstance(timeend,str) else timeend.isoformat()
        response = requests.get("%s/obs/%s/series/%i" % (self.url, tipo, series_id),
            params = params,
            headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed for series tipo: %s, id: %s. message: %s" % (tipo, series_id, response.text))
        json_response = response.json()
        return json_response

    def createObservaciones(
        self,
        data : Union[pandas.DataFrame, list],
        series_id : int,
        column : str= "valor",
        tipo : str = "puntual", 
        timeSupport : timedelta = None,
        use_proxy : bool = False
        ) -> list:
        """Create observations

        Args:
            data (Union[pandas.DataFrame, list]): Observations DataFrame or list
            series_id (int): series identifier
            column (str, optional): If data is a DataFrame, name of the column containing the values. Defaults to "valor".
            tipo (str, optional): geometry type (puntual, areal, raster). Defaults to "puntual".
            timeSupport (timedelta, optional): Observation time support. Used to set timeend. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            list: list of created observations
        """
        if isinstance(data,pandas.DataFrame):
            data = observacionesDataFrameToList(data,series_id,column,timeSupport)
        [validate(x,"Observacion") for x in data]
        url = "%s/obs/%s/series/%i/observaciones" % (self.url, tipo, series_id) if series_id is not None else "%s/obs/%s/observaciones" % (self.url, tipo)
        response = requests.post(url, json = {
                "observaciones": data
            }, headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readCalibrado(
        self,
        cal_id : int,
        use_proxy : bool = False
        ) -> dict:
        """Retrieve simulation configuration ("calibrado")

        Args:
            cal_id (int): Identifier
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: _description_
        """
        url = "%s/sim/calibrados/%i" % (self.url, cal_id)
        response = requests.get(url,headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: status: %i, message: %s" % (response.status_code, response.text))
        json_response = response.json()
        return json_response

    def createCorrida(
        self,
        data : dict,
        cal_id : int = None,
        use_proxy : bool = False
        ) -> dict:
        """Create simulation run

        Args:
            data (dict): Must validate against Corrida schema
            cal_id (int, optional): simulation configuration identifier. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: if cal_id is missing from args and from data
            Exception: Request failed if response status code is not 200

        Returns:
            dict: created simulation run
        """
        validate(data,"Corrida")
        cal_id = cal_id if cal_id is not None else data["cal_id"] if "cal_id" in data else None
        if cal_id is None:
            raise Exception("Missing parameter cal_id")
        url = "%s/sim/calibrados/%i/corridas" % (self.url, cal_id)
        response = requests.post(url, json = data, headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        logging.debug("createCorrida url: %s" % response.url)
        if response.status_code != 200:
            raise Exception("request failed: status: %i, message: %s" % (response.status_code, response.text))
        json_response = response.json()
        return json_response

    def readVar(
        self,
        var_id : int,
        use_proxy : bool = False
        ) -> dict:
        """Retrieve variable

        Args:
            var_id (int): Identifier
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.

        Raises:
            Exception: Request failed if response status code is not 200

        Returns:
            dict: the retrieved variable
        """
        response = requests.get("%s/obs/variables/%i" % (self.url, var_id),
            headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        return json_response

    def readSerieProno(
        self,
        series_id : int,
        cal_id : int,
        timestart : datetime = None,
        timeend : datetime = None,
        use_proxy : bool = False,
        cor_id : int = None,
        forecast_date : datetime = None,
        qualifier : str = None
        ) -> dict:
        """
        Reads prono serie from a5 API
        if forecast_date is not None, cor_id is overwritten by first corridas match
        returns Corridas object { series_id: int, cor_id: int, forecast_date: str, pronosticos: [{timestart:str,valor:float},...]}

        Args:
            series_id (int): series identifier
            cal_id (int): simulation configuration identifier
            timestart (datetime, optional): begin timestamp. Defaults to None.
            timeend (datetime, optional): end timestamp. Defaults to None.
            use_proxy (bool, optional): Perform request through proxy. Defaults to False.
            cor_id (int, optional): simulation run identifier. Defaults to None.
            forecast_date (datetime, optional): execution timestamp. Defaults to None.
            qualifier (str, optional): simulations qualifier (used to discriminate between simulations of the same series and timestamp, for example, from different ensemble members). Defaults to None. If 'all', returns all qualifiers (not only the first match). In the latter case, 'pronosticos' property of the return value is a list of dicts (one for each qualifier) with:
            - qualifier : str
            - pronosticos : list of time-value pairs
            

        Raises:
            Exception: Request failed if status code is not 200

        Returns:
            dict : a forecast run 
        """
        params = {}
        if forecast_date is not None:
            corridas_response = requests.get("%s/sim/calibrados/%i/corridas" % (self.url, cal_id),
                params = {
                    "forecast_date": forecast_date if isinstance(forecast_date,str) else forecast_date.isoformat()
                },
                headers = {'Authorization': 'Bearer ' + self.token},
                proxies = self.proxy_dict if use_proxy else None
            )
            if corridas_response.status_code != 200:
                raise Exception("request failed: %s" % corridas_response.text)
            corridas = corridas_response.json()
            if len(corridas):
                cor_id = corridas[0]["cor_id"]
            else:
                print("Warning: series %i from cal_id %i at forecast_date %s not found" % (series_id,cal_id,forecast_date))
                return {
                "series_id": series_id,
                "pronosticos": []
            }
        if timestart is not None and timeend is not None:
            params = {
                "timestart": timestart if isinstance(timestart,str) else timestart.isoformat(),
                "timeend": timeend if isinstance(timestart,str) else timeend.isoformat(),
                "series_id": series_id
            }
        if qualifier is not None and qualifier != 'all':
            params["qualifier"] = qualifier
        params["includeProno"] = True
        url = "%s/sim/calibrados/%i/corridas/last" % (self.url, cal_id)
        if cor_id is not None:
            url = "%s/sim/calibrados/%i/corridas/%i" % (self.url, cal_id, cor_id)
        response = requests.get(url,
            params = params,
            headers = {'Authorization': 'Bearer ' + self.token},
            proxies = self.proxy_dict if use_proxy else None
        )
        if response.status_code != 200:
            raise Exception("request failed: %s" % response.text)
        json_response = response.json()
        if "series" not in json_response:
            print("Warning: series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": series_id,
                "qualifier": None,
                "pronosticos": []
            }
        if not len(json_response["series"]):
            print("Warning: series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": series_id,
                "qualifier": None,
                "pronosticos": []
            }
        if qualifier is not None and qualifier == 'all':
            pronosticos = []
            for member in json_response["series"]:
                pronosticos.append({
                    "qualifier": member["qualifier"],
                    "pronosticos": [ observacionTupleToDict(x) for x in member["pronosticos"] ]
                })
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": json_response["series"][0]["series_id"],
                "pronosticos": pronosticos
            }
        if "pronosticos" not in json_response["series"][0]:
            print("Warning: pronosticos from series %i from cal_id %i not found" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": json_response["series"][0]["series_id"],
                "qualifier": json_response["series"][0]["qualifier"],
                "pronosticos": []
            }
        if not len(json_response["series"][0]["pronosticos"]):
            print("Warning: pronosticos from series %i from cal_id %i is empty" % (series_id,cal_id))
            return {
                "forecast_date": json_response["forecast_date"],
                "cal_id": json_response["cal_id"],
                "cor_id": json_response["cor_id"],
                "series_id": json_response["series"][0]["series_id"],
                "qualifier": json_response["series"][0]["qualifier"],
                "pronosticos": []
            }
        json_response["series"][0]["pronosticos"] = [ observacionTupleToDict(x) for x in json_response["series"][0]["pronosticos"]] # "series_id": series_id, "timeend": x[1] "qualifier":x[3]
        return {
            "forecast_date": json_response["forecast_date"],
            "cal_id": json_response["cal_id"],
            "cor_id": json_response["id"] if "id" in json_response else json_response["cor_id"],
            "series_id": json_response["series"][0]["series_id"],
            "qualifier": json_response["series"][0]["qualifier"] if "qualifier" in json_response["series"][0] else None,
            "pronosticos": json_response["series"][0]["pronosticos"]
        }

## AUX functions

def observacionesDataFrameToList(
    data : pandas.DataFrame,
    series_id : int,
    column : str = "valor",
    timeSupport : timedelta = None
    ) -> List[dict]:
    """Convert Observations DataFrame to list of dict

    Args:
        data (pandas.DataFrame): dataframe con índice tipo datetime y valores en columna "column"
        series_id (int): Series identifier
        column (str, optional): Column that contains the values. Defaults to "valor".
        timeSupport (timedelta, optional): Time support of the observation. Used to set timeend. Defaults to None.

    Raises:
        Exception: Column column not found in data

    Returns:
        List[dict]: Observations
    """
    # data: dataframe con índice tipo datetime y valores en columna "column"
    # timeSupport: timedelta object
    if data.index.dtype.name != 'datetime64[ns, America/Argentina/Buenos_Aires]':
        data.index = data.index.map(util.tryParseAndLocalizeDate)
    # raise Exception("index must be of type datetime64[ns, America/Argentina/Buenos_Aires]'")
    if column not in data.columns:
        raise Exception("column %s not found in data" % column)
    data = data.sort_index()
    data["series_id"] = series_id
    data["timeend"] = data.index.map(lambda x: x.isoformat()) if timeSupport is None else data.index.map(lambda x: (x + timeSupport).isoformat())
    data["timestart"] = data.index.map(lambda x: x.isoformat()) # strftime('%Y-%m-%dT%H:%M:%SZ') 
    data["valor"] = data[column]
    data = data[["series_id","timestart","timeend","valor"]]
    return data.to_dict(orient="records")

def observacionTupleToDict(x : tuple):
    return { 
        "timestart": x[0], 
        "valor": x[2]
    } if type(x) == list or type(x) == tuple else {
        "timestart": x["timestart"], 
        "valor": x["valor"]
    }

def observacionesListToDataFrame(
    data: list, 
    tag: str = None
    ) -> pandas.DataFrame:
    """Convert observaciones list to DataFrame

    Args:
        data (list): Observaciones
        tag (str, optional): String to set in tag column. Defaults to None.

    Raises:
        Exception: Empty list

    Returns:
        pandas.DataFrame: A DataFrame with datetime index and float column "valor". If tag was set, a "tag" column is added
    """
    if len(data) == 0:
        raise Exception("empty list")
    data = pandas.DataFrame.from_dict(data)
    data["valor"] = data["valor"].astype(float)
    data.index = data["timestart"].apply(util.tryParseAndLocalizeDate)
    data.sort_index(inplace=True)
    if tag is not None:
        data["tag"] = tag
        return data[["valor","tag"]]
    else:
        return data[["valor",]]

def createEmptyObsDataFrame(
    extra_columns : dict = None
    ) -> pandas.DataFrame:
    """Create Observations DataFrame with no rows

    Args:
        extra_columns (dict, optional): Additional columns. Keys are the column names, values are the column types. Defaults to None.

    Returns:
        pandas.DataFrame: Observations dataframe
    """
    data = pandas.DataFrame({
        "timestart": pandas.Series(dtype='datetime64[ns, America/Argentina/Buenos_Aires]'),
        "valor": pandas.Series(dtype="float")
    })
    cnames = ["valor"]
    if extra_columns is not None:
        for cname in extra_columns:
            data[cname] = pandas.Series(dtype=extra_columns[cname])
            cnames.append(cname)
    data.index = data["timestart"]
    return data[cnames]

## EJEMPLO
'''
import pydrodelta.a5 as a5
import pydrodelta.util as util
# lee serie de api a5
serie = a5.readSerie(31532,"2022-05-25T03:00:00Z","2022-06-01T03:00:00Z")
serie2 = a5.readSerie(26286,"2022-05-01T03:00:00Z","2022-06-01T03:00:00Z")
# convierte observaciones a dataframe 
obs_df = a5.observacionesListToDataFrame(serie["observaciones"]) 
obs_df2 = a5.observacionesListToDataFrame(serie["observaciones"]) 
# crea index regular
new_index = util.createRegularDatetimeSequence(obs_df.index,timedelta(days=1))
# crea index regular a partir de timestart timeend
timestart = util.tryParseAndLocalizeDate("1989-10-14T03:00:00.000Z")
timeend = util.tryParseAndLocalizeDate("1990-03-10T03:00:00.000Z")
new_index=util.createDatetimeSequence(timeInterval=timedelta(days=1),timestart=timestart,timeend=timeend,timeOffset=timedelta(hours=6))
# genera serie regular
reg_df = util.serieRegular(obs_df,timeInterval=timedelta(hours=12))
reg_df2 = util.serieRegular(obs_df2,timeInterval=timedelta(hours=12),interpolation_limit=1)
# rellena nulos con otra serie
filled_df = util.serieFillNulls(reg_df,reg_df2)
# convierte de dataframe a lista de dict
obs_list = a5.observacionesDataFrameToList(obs_df,series_id=serie["id"])
# valida observaciones
for x in obs_list:
    a5.validate(x,"Observacion")
# sube observaciones a la api a5
upserted = a5.createObservaciones(obs_df,series_id=serie["id"])
'''