from pydrodelta.config import config
from pydrodelta.arima import adjustSeriesArima
import dateutil.parser
from dateutil.relativedelta import relativedelta
import pytz
from dateutil import tz
localtz = pytz.timezone('America/Argentina/Buenos_Aires')
import pandas
from datetime import timedelta, datetime
# from zoneinfo import ZoneInfo
import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import logging
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import csv
import os.path
from typing import Union, Tuple, List, Literal
import random
DataFrame = pandas.DataFrame
DatetimeIndex = pandas.DatetimeIndex
Series = pandas.Series
import numpy as np

def interval2timedelta(interval : Union[dict,float,relativedelta]):
    """Parses duration dict or number of days into dateutil.relativedelta object
    
    Parameters:
    -----------
    interval : dict or float (decimal number of days) or relativedelta
        If dict, allowed keys are:
        - days
        - seconds
        - microseconds
        - minutes
        - hours
        - weeks
    
    Returns:
    --------
    duration : dateutil.relativedelta.relativedelta

    Examples:

    ```
    interval2timedelta({"hours":1, "minutes": 30})
    interval2timedelta(1.5/24)
    ```
    """
    if isinstance(interval, relativedelta):
        return interval
    if isinstance(interval,(float,int)):
        return relativedelta(days=interval)
    if isinstance(interval, dict):
        days = 0
        seconds = 0
        microseconds = 0
        minutes = 0
        hours = 0
        weeks = 0
        months = 0
        for k in interval:
            if k == "microseconds" or k == "microsecond":
                microseconds = microseconds + interval[k]
            if k == "milliseconds" or k == "millisecond":
                microseconds = microseconds + interval[k] * 1000
            elif k == "seconds" or k == "second":
                seconds = interval[k]
            elif k == "minutes" or k == "minute":
                minutes = interval[k]
            elif k == "hours" or k == "hour":
                hours = interval[k]
            elif k == "days" or k == "day":
                days = interval[k]
            elif k == "weeks" or k == "week":
                weeks = interval[k]
            elif k == "months" or k == "months":
                months = interval[k]
        return relativedelta(days=days, seconds=seconds, microseconds=microseconds, minutes=minutes, hours=hours, weeks=weeks, months=months)
    else:
        raise TypeError("Invalid type for time interval: %s" % type(interval))

def interval2epoch(interval):
    seconds = 0
    for k in interval:
        if k == "milliseconds" or k == "millisecond":
            seconds = seconds + interval[k] * 0.001
        elif k == "seconds" or k == "second":
            seconds = seconds + interval[k]
        elif k == "minutes" or k == "minute":
            seconds = seconds + interval[k] * 60
        elif k == "hours" or k == "hour":
            seconds = seconds + interval[k] * 3600
        elif k == "days" or k == "day":
            seconds = seconds + interval[k] * 86400
        elif k == "weeks" or k == "week":
            seconds = seconds + interval[k] * 86400 * 7
        elif k == "months" or k == "month" or k == "mon":
            seconds = seconds + interval[k] * 86400 * 31
        elif k == "years" or k == "year":
            seconds = seconds + interval[k] * 86400 * 365
    return seconds

def tryParseAndLocalizeDate(
        date_string : Union[str,float,datetime,tuple],
        timezone : str='America/Argentina/Buenos_Aires'
    ) -> datetime:
    """
    Datetime parser. If duration is provided, computes date relative to now.

    Parameters:
    -----------
    date_string : str or float or datetime.datetime
        For absolute date: ISO-8601 datetime string or datetime.datetime or (year,month,date) tuple.
        For relative date: dict (duration key-values) or float (decimal number of days)
    
    timezone : str
        Time zone string identifier. Default: America/Argentina/Buenos_Aires
    
    Returns:
    --------
    datetime.datetime

    Examples:
    ---------
    ``` 
    tryParseAndLocalizeDate("2024-01-01T03:00:00.000Z")
    tryParseAndLocalizeDate(1.5)
    tryParseAndLocalizeDate({"days":1, "hours": 12}, timezone = "Africa/Casablanca")
    tryParseAndLocalizeDate((2000,1,1))
    ```
    """
    
    date = dateutil.parser.isoparse(date_string) if isinstance(date_string,str) else date_string
    is_from_interval = False
    if isinstance(date,dict):
        date = datetime.now() + relativedelta(**date)
        is_from_interval = True
    elif isinstance(date,(int,float)):
        date = datetime.now() + relativedelta(days=date)
        is_from_interval = True
    elif isinstance(date, tuple):
        if len(date) < 3:
            raise ValueError("Invalid date tuple: missing items (3 required)")
        date = datetime(*date)
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        try:
            tz = pytz.timezone(timezone)
            date = tz.localize(date)
            # date = date.replace(tzinfo = pytz.timezone(timezone)) # ZoneInfo(timezone))
        except pytz.exceptions.NonExistentTimeError:
            logging.warning("NonexistentTimeError: %s" % str(date))
            return None
    else:
        date = date.astimezone(pytz.timezone(timezone)) # ZoneInfo(timezone))
    return date # , is_from_interval

def roundDownDate(date : datetime,timeInterval : relativedelta,timeOffset : relativedelta=None) -> datetime:
    if timeInterval.microseconds == 0:
        date = date.replace(microsecond=0)
    if timeInterval.seconds % 60 == 0:
        date = date.replace(second=0)
    if timeInterval.seconds % 3600 == 0:
        date = date.replace(minute=0)
    if timeInterval.seconds == 0 and timeInterval.days >= 1:
        date = date.replace(hour=0)
        if timeOffset is not None:
            date = date + timeOffset
    return date

def roundDate(date : datetime,timeInterval : relativedelta,timeOffset : relativedelta=None, to="up") -> datetime:
    date_0 = tryParseAndLocalizeDate(datetime.combine(date.date(),datetime.min.time()))
    if timeOffset is not None:
        date_0 = date_0 + timeOffset 
    while date_0 < date:
        date_0 = date_0 + timeInterval
    if date_0 == date:
        return date_0
    elif to == "up":
        return date_0
    else:
        return date_0 - timeInterval

def createDatetimeSequence(
    datetime_index : pandas.DatetimeIndex=None, 
    timeInterval : Union[relativedelta,dict,int,timedelta] = relativedelta(days=1), 
    timestart : Union[datetime,tuple,str] = None, 
    timeend : Union[datetime,tuple,str] = None, 
    timeOffset : Union[relativedelta,dict] = None
    ) -> pandas.DatetimeIndex:
    #Fechas desde timestart a timeend con un paso de timeInterval
    #data: dataframe con index tipo datetime64[ns, America/Argentina/Buenos_Aires]
    #timeOffset sólo para timeInterval n days
    if datetime_index is None and (timestart is None or timeend is None):
        raise Exception("Missing datetime_index or timestart+timeend")
    timestart = tryParseAndLocalizeDate(timestart) if timestart is not None else datetime_index.min()
    timeInterval = relativedelta(**timeInterval) if isinstance(timeInterval,dict) else timedelta_to_relativedelta(timeInterval) if isinstance(timeInterval,timedelta) else timeInterval
    timeOffset = relativedelta(**timeOffset) if isinstance(timeOffset,dict) else timeOffset
    timestart = roundDate(timestart,timeInterval,timeOffset,"up")
    timeend = tryParseAndLocalizeDate(timeend) if timeend  is not None else datetime_index.max()
    timeend = roundDate(timeend,timeInterval,timeOffset,"down")
    timezone = pytz.timezone("America/Argentina/Buenos_Aires")
    is_subdaily = timeInterval.hours > 0 or timeInterval.minutes > 0 or timeInterval.seconds > 0 or timeInterval.microseconds > 0
    if not is_subdaily:
        if timestart.day == 1 and timeInterval.months > 0:
            freq = "%iMS" % timeInterval.months
        elif timestart.day == 1 and timestart.month == 1 and timeInterval.years > 0:
            freq = "%iYS" % timeInterval.years 
        elif timeInterval.days > 0:
            freq = "%iD" % timeInterval.days
        dts_utc = pandas.date_range(
            start=timestart.astimezone(tz.UTC), 
            end=timeend.astimezone(tz.UTC), 
            freq = freq
        )
        if timeOffset is not None:
            return DatetimeIndex([timezone.localize(datetime(dt.year,dt.month,dt.day,timeOffset.hours,timeOffset.minutes,timeOffset.seconds)) for dt in dts_utc])
        else:
            return DatetimeIndex([timezone.localize(datetime(dt.year,dt.month,dt.day)) for dt in dts_utc])
    else:
        freq = pandas.DateOffset(
                years=timeInterval.years,
                months=timeInterval.months,
                weeks=timeInterval.weeks,
                days=timeInterval.days, 
                hours=timeInterval.hours, 
                minutes = timeInterval.minutes,
                seconds = timeInterval.seconds,
                microseconds = timeInterval.microseconds
            )
        return pandas.date_range(
            start=timestart, 
            end=timeend, 
            freq=freq
        ) # .tz_convert(timestart.tzinfo)

def f1(row,column="valor",timedelta_threshold : timedelta=None):
    now = datetime.now()
    a = now - row["diff_with_next"]
    b = now + timedelta_threshold
    if a > b:
        return row[column]
    else:
        return row["interpolated_backward"]

def f2(row,column="valor",timedelta_threshold : timedelta=None):
    now = datetime.now()
    a = now + row["diff_with_previous"]
    b = now + timedelta_threshold
    if a > b:
        return row[column]
    else:
        return row["interpolated_forward"]

def f3(row,column="valor",timedelta_threshold : timedelta=None):
    if pandas.isna(row["interpolated_forward_filtered"]):
        return row["interpolated_backward_filtered"]
    else:
        return row["interpolated_forward_filtered"]

def f4(row,column="valor",tag_column="tag"):
    if pandas.isna(row["interpolated_final"]):
        return row[tag_column]
    elif pandas.isna(row[column]):
        return "interpolated"
    else:
        return row[tag_column]

def serieRegular(
    data : pandas.DataFrame, 
    time_interval : relativedelta, 
    timestart : datetime  = None, 
    timeend : datetime = None, 
    time_offset : relativedelta = None, 
    column : str = "valor", 
    interpolate : bool = True, 
    interpolation_limit : Union[int,timedelta] = 1,
    tag_column : str = None, 
    extrapolate : bool = False,
    agg_func : str = None,
    extrapolate_function : "str" = "linear",
    extrapolate_train_length : int = 5
    ) -> pandas.DataFrame:
    """
    genera serie regular y rellena nulos interpolando
    if interpolate=False, interpolates only to the closest timestep of the regular timeseries. If observation is equidistant to preceding and following timesteps it interpolates to both. If agg_func is not None,   aggregates column column of data using the selected aggregation function grouping by time step (in this case, interpolation is not performed)
    If extrapolate is set to True, extrapolates using extrapolate_function ("linear", "last") up to extrapolation_limit steps

    Args:
        data(DataFrame): input data to be regularized
        time_interval(relativedelta): desired time step of the regularized output
        timestart(datetime, optional): begin date of regularized output. If not set, begin date of data is used
        timeend(datetime, optional): end date of regularized output. If not set, end date of data is used
        time_offset(relativedelta, optional): time offset of regularized output. If not set, begin time of data is used
        column(str, optional): column name of data to extract. Defaults to "valor"
        interpolate(bool, optional): Interpolate missing rows. Defaults to True. If agg_func is set, interpolation is not performed
        interpolation_limit(int,, optional): Number of steps to interpolate. Defaults to 1. If agg_func is set, interpolation is not performed
        tag_column(str, optional): name of the tag column. If not set, output will not have a tag column
        extrapolate(bool, optional): enable extrapolation up to interpolation_limit steps. Defaults to False
        agg_func(str, optional): aggregation function. See aggregateByTimestep()
        extrapolate_function: extrapolation function: "linear" (default): fit linear regression, "last": repeat last value 
        extrapolate_train_length: use this number of  last values to fit the reggresion line used for extrapolation 

    Returns:
      DataFrame - time step regularized data (either interpolated or aggregated) 
    """
    df_regular = DataFrame(index = createDatetimeSequence(data.index, time_interval, timestart, timeend, time_offset))
    df_regular.index.rename('timestart', inplace=True)
    if agg_func is not None:
        agg_serie = aggregateByTimestep(
            data,
            df_regular.index,
            time_interval,
            column = column,
            agg_func = agg_func
        )
        df_regular[column] = agg_serie
        if tag_column:
            df_regular[tag_column] = agg_func
        return df_regular
    if not len(data):
        df_regular[column] = None
        if tag_column is not None:
            df_regular[tag_column] = None
        return df_regular
    df_join = df_regular.join(data, how = 'outer')
    df_join.index.name = "timestart"
    if interpolate:
        # Interpola
        min_obs_date, max_obs_date = (df_join[~pandas.isna(df_join[column])].index.min(),df_join[~pandas.isna(df_join[column])].index.max())
        if isinstance(interpolation_limit, timedelta):
            df_join["interpolated"] = interpolate_or_copy_closest(df_join[column], interpolation_limit)
        else:
            # extrapolate before so that only noninterpolated points are used in regression
            if extrapolate and extrapolate_function == "linear":
                extrapolated = extrapolate_linear(df_join, "valor", extrapolation_limit=interpolation_limit, train_length = extrapolate_train_length)
            df_join["interpolated"] = df_join[column].interpolate(method='time',limit=interpolation_limit,limit_direction='both',limit_area=None if extrapolate and extrapolate_function == "last" else 'inside')
        if extrapolate and extrapolate_function == "linear":
            # fill interpolated nans with extrapolated
            df_join["interpolated"] = df_join["interpolated"].fillna(extrapolated["valor"])
        if tag_column is not None:
            # print("columns: " + df_join.columns)
            df_join[tag_column] = [x[tag_column] if pandas.isna(x["interpolated"]) else "extrapolated" if i < min_obs_date or i > max_obs_date else "interpolated" if pandas.isna(x[column]) else x[tag_column] for (i, x) in df_join.iterrows()]
        df_join[column] = df_join["interpolated"]
        del df_join["interpolated"]
        for c in df_join.columns:
            if c == column:
                continue
            if tag_column is not None and c == tag_column:
                continue
            df_join[c] = df_join[c].interpolate(method='time',limit=interpolation_limit,limit_direction='both',limit_area=None if extrapolate and extrapolate_function == "last" else 'inside')
        df_regular = df_regular.join(df_join, how = 'left')
    else:
        timedelta_threshold = relativedelta_to_timedelta(time_interval) * 0.5 # takes half time interval as maximum time distance for interpolation
        df_regular = regularizeColumn(df_regular,df_join,timedelta_threshold, column, tag_column)
        for c in df_join.columns:
            if c == column:
                continue
            if tag_column is not None and c == tag_column:
                continue
            df_regular = regularizeColumn(df_regular,df_join,timedelta_threshold,c)
    return df_regular

def regularizeColumn(
    df_regular : pandas.DataFrame,
    df_join : pandas.DataFrame, 
    timedelta_threshold : timedelta, 
    column : str = "valor",
    tag_column : str = None
    ) -> pandas.DataFrame:
    # if column == "tag":
    #     logging.warning("interpolating tag")
    # df_join = df_join.reset_index()
    # df_join["diff_with_previous"] = df_join["timestart"].diff()
    # df_join["diff_with_next"] = df_join["timestart"].diff(periods=-1)
    # df_join = df_join.set_index("timestart")
    # df_join["interpolated_backward"] = df_join[column].interpolate(method='time',limit=1,limit_direction='backward',limit_area=None)
    # df_join["interpolated_forward"] = df_join[column].interpolate(method='time',limit=1,limit_direction='forward',limit_area=None)
    # df_join["interpolated_backward_filtered"] = df_join.apply(lambda row: f1(row,column,timedelta_threshold),axis=1) #[ x[column] if -x["diff_with_next"] > timedelta_threshold else x.interpolated_backward for (i,x) in df.iterrows()]
    # df_join["interpolated_forward_filtered"] = df_join.apply(lambda row: f2(row,column,timedelta_threshold),axis=1)#[ x[column] if x["diff_with_previous"] > timedelta_threshold else x.interpolated_forward for (i,x) in df.iterrows()]
    # df_join["interpolated_final"] = df_join.apply(lambda row: f3(row,column,timedelta_threshold),axis=1) #[x.interpolated_backward_filtered if pandas.isna(x.interpolated_forward_filtered) else x.interpolated_forward_filtered for (i,x) in df.iterrows()]
    df_ = df_join.copy()
    df_["interpolated_final"] = interpolate_or_copy_closest(df_[column], timedelta_threshold)
    if tag_column is not None:
        df_["new_tag"] = df_.apply(lambda row: f4(row,column,tag_column),axis=1) #[x[tag_column] if pandas.isna(x.interpolated_final) else "interpolated" if pandas.isna(x.valor) else x[tag_column] for (i,x) in df_join.iterrows()]
        df_regular = df_regular.join(df_[["interpolated_final","new_tag"]].rename(columns={"interpolated_final":column,"new_tag":tag_column}), how = 'left')
    else:
        df_regular = df_regular.join(df_[["interpolated_final",]].rename(columns={"interpolated_final":column}), how = 'left')
    return df_regular    

def f5(row,column="valor",tag_column="tag",min_obs_date=None,max_obs_date=None):
    if pandas.isna(row["interpolated"]):
        return row[tag_column]
    elif row.name < min_obs_date or row.name > max_obs_date:
        return "extrapolated"
    elif pandas.isna(row[column]):
        return "interpolated"
    else:
        return row[tag_column]

def interpolateData(
        data : pandas.DataFrame,
        column : str = "valor",
        tag_column : str = None,
        interpolation_limit : int = 1,
        extrapolate : bool = False
        ) -> pandas.DataFrame:
    min_obs_date, max_obs_date = (data[~pandas.isna(data[column])].index.min(),data[~pandas.isna(data[column])].index.max())
    data["interpolated"] = data[column].interpolate(method='time',limit=interpolation_limit,limit_direction='both',limit_area=None if extrapolate else 'inside')
    if tag_column is not None:
        data[tag_column] = data.apply(lambda row: f5(row,column,tag_column,min_obs_date,max_obs_date),axis=1)#[x[tag_column] if pandas.isna(x["interpolated"]) else "extrapolated" if i < min_obs_date or i > max_obs_date else "interpolated" if pandas.isna(x[column]) else x[tag_column] for (i, x) in data.iterrows()]
    data[column] = data["interpolated"]
    del data["interpolated"]
    return data

def serieFillNulls(data : pandas.DataFrame, other_data : pandas.DataFrame, column : str="valor", other_column : str="valor", fill_value : float=None, shift_by : int=0, bias : float=0, extend=False, tag_column=None):
    """
    rellena nulos de data con valores de other_data donde coincide el index. Opcionalmente aplica traslado rígido en x (shift_by: n registros) y en y (bias: float)

    si extend=True el índice del dataframe resultante será la unión de los índices de data y other_data (caso contrario será igual al índice de data)
    """
    # logging.debug("before. data.index.name: %s. other_data.index.name: %s" % (data.index.name, other_data.index.name))
    mapper = {}
    mapper[other_column] = "valor_fillnulls"
    how = "outer" if extend else "left"
    if tag_column is not None:
        mapper[tag_column] = "tag_fillnulls"
        data = data.join(other_data[[other_column,tag_column]].rename(mapper,axis=1), how = how)
        data[column] = data[column].fillna(data["valor_fillnulls"].shift(shift_by, axis = 0) + bias)
        data[tag_column] = data[tag_column].fillna(data["tag_fillnulls"].shift(shift_by, axis = 0))
        if fill_value is not None:
            data[column] = data[column].fillna(fill_value)
            data[tag_column] = data[tag_column].fillna("filled")
        del data["valor_fillnulls"]
        del data["tag_fillnulls"]
    else:
        data = data.join(other_data[[other_column,]].rename(mapper,axis=1), how = how)
        data[column] = data[column].fillna(data["valor_fillnulls"].shift(shift_by, axis = 0) + bias)
        del data["valor_fillnulls"]
        if fill_value is not None:
            data[column] = data[column].fillna(fill_value)
    # logging.debug("after. data.index.name: %s. other_data.index.name: %s" % (data.index.name, other_data.index.name))
    return data

def serieMovingAverage(
    obs_df : pandas.DataFrame,
    offset : relativedelta,
    column : str = "valor",
    tag_column : str = None
    ) -> pandas.DataFrame:
    data = pandas.DataFrame(obs_df[column].rolling(offset, min_periods=1).mean())
    if tag_column is not None:
        data.insert(1,'tag', [x if not pandas.isna(x) else "moving_average" for x in obs_df[tag_column]], True)
    return data

def applyTimeOffsetToIndex(obs_df,x_offset):
    original_df = obs_df[["valor",]]
    del original_df["valor"]
    obs_df.index = [x + x_offset for x in obs_df.index]
    obs_df = original_df.join(obs_df,how='outer')
    obs_df.interpolate(method='time',limit=1,inplace=True)
    obs_df = original_df.join(obs_df,how='left')
    return obs_df


def removeOutliers(data : pandas.DataFrame,limite_outliers,column="valor"):
    '''
    remove outliers inline and return outliers data frame
    '''
    # print('Detecta Outliers:')
    limit_inf = limite_outliers[0]
    limit_sup = limite_outliers[1]
    # print("Limite superior",round(limit_sup,2))
    # print("Limite inferior",round(limit_inf,2)) 
    # Finding the Outliers
    outliers_iqr = data[( data[column] < limit_inf) | (data[column] > limit_sup)]
    logging.debug('Cantidad de outliers: %i' % len(outliers_iqr))
    data[column] = np.where(data[column]>limit_sup,np.nan,
                   np.where(data[column]<limit_inf,np.nan,
                   data[column]))
    return outliers_iqr

def detectJumps(data : pandas.DataFrame,lim_jump,column="valor"):
    '''
    returns jump rows as data frame
    '''
    # print('Detecta Saltos:')	
    data_ = data[[column,]].copy()
    VecDif = abs(np.diff(data_[column].values))
    VecDif = np.append([0,],VecDif)
    coldiff = 'Diff_Valor'
    data_[coldiff] = VecDif
    # print('Limite Salto (m): ',lim_jump)
    df_saltos = data_[data_[coldiff] > lim_jump].sort_values(by=coldiff)
    logging.debug('Cantidad de Saltos: %i' % len(df_saltos))
    del data_[coldiff]
    return df_saltos

def adjustSeries(
        sim_df : pandas.DataFrame,
        truth_df : pandas.DataFrame,
        method : str = "lfit",
        plot : bool = True,
        return_adjusted_series : bool = True,
        tag_column : str = None,
        title : str = None,
        warmup : int = None,
        tail : int = None,
        sim_range : Tuple[float,float] = None,
        covariables : List[str] = ["valor"],
        return_df : bool = False,
        drop_warmup : bool = False
        )  -> Union[dict,Tuple[pandas.Series, pandas.Series, dict]]:
    """Adjust sim_df with truth_df by means of a linear regression

    Args:
        sim_df (pandas.DataFrame): data to adjust
        truth_df (pandas.DataFrame): truth data to adjust sim_df with 
        method (str, optional): Regression method. Defaults to "lfit".
        plot (bool, optional): Plot data. Defaults to True.
        return_adjusted_series (bool, optional): If True, return tuple of (adjusted values (pandas.Series), adjusted series tag (pandas.Series), fit result stats (dict)). Else return only fit result stats (dict) . Defaults to True.
        tag_column (str, optional): Name of the tag column. Defaults to None.
        title (str, optional): Title of the plot. Defaults to None.
        warmup (int, optional): Number of initial rows to skip for the fit procedure. Defaults to None.
        tail (int, optional): Number of final steps to use for the fit procedure (discard the rest).
        sim_range (Tuple[float,float],optional): Select data pairs where sim is within this range.
        covariables (List[float],optional): Column names to extract from sim_df to be used as explanatory variables
        return_df Bool = True: Return DataFrame instead of Series
        drop_warmup Bool = False: eliminate warmup steps from output

    Raises:
        ValueError: unknown method

    Returns:
        Union[dict,Tuple[pandas.Series, pandas.Series, dict]]: If return_adjusted_seris is True, it returns a tuple of (adjusted values (pandas.Series), adjusted series tag (pandas.Series), fit result stats (dict)). Else it returns only fit result stats (dict)
    """
    truth_warm = truth_df.iloc[warmup:].copy() if warmup is not None else truth_df
    truth_warm = truth_warm.tail(tail) if tail is not None else truth_warm
    data = truth_warm.join(sim_df[covariables],how="outer" if method == "arima" else "left",rsuffix="_sim")
    covariables_sim = ["%s_sim" % x if x == "valor" else x for x in covariables]
    if sim_range is not None:
        data = data.loc[(data[covariables_sim[0]] >= sim_range[0]) & (data[covariables_sim[0]] <= sim_range[1])].copy()
    if method == "lfit":
        try:
            lr, quant_Err, r2, coef, intercept, train, mse, rse =  ModelRL(data,"valor",covariables_sim)
        except ValueError as e:
            raise ValueError("Linear regression error: %s" % str(e))
        # logging.info(quant_Err)
        # Prediccion
        aux_df = sim_df.copy().dropna()
        predict = lr.predict(aux_df[covariables].values)
        aux_df["adj"] = predict
        a_cols = [c for c in ["valor","tag","adj"] if c in aux_df]
        t_cols = [c for c in ["valor","tag"] if c in truth_warm]
        aux_df = aux_df[a_cols].rename(columns={"valor":"valor_sim","tag":"tag_sim"}).join(truth_warm[t_cols].rename(columns={"valor":"valor_obs","tag":"tag_obs"}),how='outer')
        figtext = "r2: %.04f, coef: %s, intercept: %.04f" % (r2,",".join(["%.04f" % x for x in coef]), intercept)
        plot_columns = [c for c in ["valor_obs","valor_sim","adj"] if c in aux_df.columns]
        fitted_model = {
            "method": "lfit",
            "quant_Err": quant_Err, 
            "r2": r2, 
            "coef": coef, 
            "intercept": intercept, 
            "train": train,
            "coefficients": lr.coef_.tolist(),  # Convert numpy array to list
            "intercept": lr.intercept_
        }
        result_columns = ["adj"]
    elif method == "arima":
        arima_model, aux_df =  adjustSeriesArima(data)
        figtext = "mse: %.2e, const: %.04f, ar.L1: %.04f, ma.L1: %.04f, sigma2: %.04f" % (
            arima_model["mse"],
            arima_model["const"],
            arima_model["ar.L1"],
            arima_model["ma.L1"],
            arima_model["sigma2"]
        )
        plot_columns = [c for c in ["valor","valor_sim","adj","lower","upper"] if c in aux_df.columns]
        fitted_model = arima_model
        result_columns = ["adj", "lower", "upper"]
    else:
        raise ValueError("unknown method " + method)
    if plot:
        plt.figure(figsize=(16,8))
        plt.plot(aux_df[plot_columns]) # (data)
        plt.legend(plot_columns) # data.columns)
        if title:
            plt.title(title)
        plt.figtext(0.5, 0.01, figtext)
    if return_adjusted_series:
        return_value_0 = aux_df[result_columns] if return_df else aux_df["adj"]
        if drop_warmup:
            return_value_0 = return_value_0[warmup:]
        if tag_column is not None:
            aux_df["tag_adj"] = [None if pandas.isna(x) else "%s,adjusted" % x for x in aux_df["tag_sim"]]
            return (return_value_0, aux_df["tag_adj"],fitted_model)
        else:
            return (return_value_0, None, fitted_model)
    else:
        return fitted_model

def linearCombination(sim_df : pandas.DataFrame,params : dict,plot=True,tag_column=None) -> pandas.Series:
    '''
        sim_df: DataFrame con las covariables
        params: { intercept: float, coefficients: [float,...]
        plot: Boolean
    '''

    sim_df["predict"] = params["intercept"]
    for i in range(len(params["coefficients"])):
        sim_df["predict"] += sim_df.iloc[:,i] * params["coefficients"][i]
    if plot:
        plt.figure(figsize=(16,8))
        plt.plot(sim_df)
        plt.legend(sim_df.columns)
    if tag_column is not None:
        sim_df[tag_column] = ["%s,linear_combination" % x if ~pandas.isna(x) else None for x in sim_df[tag_column]]
        return (sim_df["predict"], sim_df[tag_column])
    else:
        return sim_df["predict"]
    
def ModelRL(data : pandas.DataFrame, varObj : str, covariables : list):
    train = data.copy()

    ## Modelo
    train = train.dropna()

    if not len(train):
        raise ValueError("No data pairs found for fit procedure")

    var_obj = varObj
    covariav = covariables

    lr = linear_model.LinearRegression()
    X_train = train[covariav]
    Y_train = train[var_obj]
    reg = lr.fit(X_train,Y_train)
    r2 = reg.score(X_train,Y_train)
    coef = reg.coef_
    intercept = reg.intercept_
    logging.info("linear model. r2: %.04f, coefs: %s, intercept: %.04f" % (r2,",".join([str(x) for x in coef]),intercept))
    # Create the test features dataset (X_test) which will be used to make the predictions.
    X_test = train[covariav].values
    # The labels of the model
    Y_test = train[var_obj].values
    Y_predictions = lr.predict(X_test)
    train['Y_predictions'] = Y_predictions
    #train['Y_predictions'] = train['h_sim'] - train['Y_predictions'] 
    residuals = Y_test - Y_predictions
    rse = np.sqrt(np.sum(residuals**2) / (len(Y_test) - 2))
    # The coefficients
    # The mean squared error
    mse = mean_squared_error(Y_test, Y_predictions)
    # The coefficient of determination: 1 is perfect prediction
    coefDet = r2_score(Y_test, Y_predictions)
    logging.debug('Coefficients B0: %.5f, coefficients: %s, Mean squared error: %.5f, r2_score: %.5f' % (lr.intercept_, ", ".join(["%.5f" % c for c in lr.coef_]), mse, coefDet))
    train['Error_pred'] =  train['Y_predictions']  - train[var_obj]
    quant_Err = train['Error_pred'].quantile([.001,.05,.95,.999])
    return lr,quant_Err,r2,coef,intercept,train, mse, rse

def lfunc_of_datetime(x : datetime, coef : float, intercept : float) -> float:
    return x.timestamp() // 10**9 * coef + intercept 

def extrapolate_linear(data : pandas.DataFrame, column : str="valor", extrapolation_limit: int = 1, train_length : int = 5) -> pandas.DataFrame:
    # get train set 
    train = data[pandas.notnull(data[column])].tail(train_length)
    if len(train) < train_length:
        raise ValueError("Not enough observations for linear regression. Required: %d" % train_length)
    # set datetime index as covariable
    train['epoch'] = train.index.astype(int) // 10**9
    model, quant_Err, r2, coef, intercept, train_ , mse, rse = ModelRL(train,varObj=column,covariables=["epoch"])
    # get index of last row with value
    last_index = train.tail(1).index[0]
    # get indexes of nans
    indexes_of_nans = data[data.index > last_index].index # .astype(float).values # & pandas.isnull(data[column])
    # limit extrapolation
    indexes_of_nans = indexes_of_nans[0:extrapolation_limit]
    # extrapolate nans using fitted coefficients # 
    data.loc[indexes_of_nans, column] = [x.timestamp() * coef[0] + intercept for x in indexes_of_nans]
    return data

def plot_prono(
    obs_df:pandas.DataFrame,
    sim_df:pandas.DataFrame,
    output_file:str,
    title:str=None,
    ydisplay:float=1,
    xytext:tuple=(-300,-200),
    ylim:tuple=(0,2.5),
    markersize:int=20,
    text_xoffset:tuple=(-8,-8),
    prono_label:str='forecasted',
    obs_label:str='observed',
    extraObs:pandas.DataFrame=None,
    extraObsLabel:str='observed 2', 
    forecast_date:datetime=None,
    errorBand:tuple=None,
    obsLine:bool=False,
    station_name:str="Station",
    thresholds:dict={}, 
    datum:float=None,
    footnote:str=None,
    tz:str="America/Argentina/Buenos_Aires",
    figsize:tuple=(14,12),
    errorBandLabel:str='error band',
    prono_annotation:str='forecast',
    obs_annotation:str='past',
    forecast_date_annotation:str='forecast date',
    x_label:str='date',
    y_label:str='value',
    datum_template_string:str=None,
    title_template_string:str="forecast at %s",
    xlim:tuple=None,
    prono_fmt='b-',
    annotate : bool = True,
    table_columns : list = ['Fecha','Nivel'],
    date_form : str = "%H hrs \n %d-%b",
    xaxis_minor_tick_hours : list = [3,9,15,21],
    error_band_fmt : Union[str,Tuple[str,str]] = 'k-',
    forecast_table : bool = True,
    footnote_height : float = 0.2,
    prono_annotation_color : str = "black",
    format : str = "png",
    adjust_results_string : str = None
    ):
    ydisplay = 1 if ydisplay is None else ydisplay
    markersize = 20 if markersize is None else markersize
    errorBandLabel = "error band" if errorBandLabel is None else errorBandLabel
    tz = "America/Argentina/Buenos_Aires" if tz is None else tz
    prono_label='forecasted' if prono_label is None else prono_label
    obs_label='observed' if obs_label is None else obs_label
    extraObsLabel='observed 2' if extraObsLabel is None else extraObsLabel
    obs_annotation='past' if obs_annotation is None else obs_annotation
    station_name="Station" if station_name is None else station_name
    # datum = 0 if datum is None else datum
    figsize=(14,12) if figsize is None else figsize
    prono_annotation='forecast' if prono_annotation is None else prono_annotation
    forecast_date_annotation='forecast date' if forecast_date_annotation is None else forecast_date_annotation
    title_template_string="forecast at %s" if title_template_string is None else title_template_string
    x_label='date' if x_label is None else x_label
    y_label = 'value' if y_label is None else y_label
    sim_df.index = sim_df.index.tz_convert(tz=tz)
    text_xoffset = (-8,-8) if text_xoffset is None else text_xoffset
    ylim = (0,2.5) if ylim is None else ylim
    thresholds = {} if thresholds is None else thresholds
    if not isinstance(obs_df,type(None)):
        obs_df.index = obs_df.index.tz_convert(tz=tz)
        # print(df_obs.index)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1)
    if title is not None:
        ax.title(title)
    prono_fmt = prono_fmt if prono_fmt is not None else 'b-'
    ax.plot(sim_df.index, sim_df['valor'], prono_fmt,label=prono_label,linewidth=3,markersize=markersize) # ,color='b'
    if not isinstance(obs_df, type(None)):
        ax.plot(obs_df.index, obs_df['valor'],'o',color='k',label=obs_label,linewidth=3)
        if obsLine:
            ax.plot(obs_df.index, obs_df['valor'],'-',color='k',linewidth=1,markersize=markersize)
    if not isinstance(extraObs,type(None)):
        extraObs.index = extraObs.index.tz_convert(tz)
        ax.plot(extraObs.index, extraObs['valor'],'o',color='grey',label=extraObsLabel,linewidth=3,alpha=0.5)
        ax.plot(extraObs.index, extraObs['valor'],'-',color='grey',linewidth=1,alpha=0.5)
    if errorBand is not None:
        if errorBand[0] not in sim_df.columns:
            raise ValueError("Error: Qualifier %s, chosen for inferior error band, missing in columns" % errorBand[0])
        if errorBand[1] not in sim_df.columns:
            raise ValueError("Error: Qualifier %s, chosen for superior error band, missing in columns" % errorBand[1])
        if type(error_band_fmt) == str and error_band_fmt == 'errorbar':
            # control error band 
            if((sim_df["valor"] - sim_df[errorBand[0]]).min() < 0):
                raise ValueError("Bad inferior error band, can't be greater than main")
            if((sim_df[errorBand[1]] - sim_df["valor"]).min() < 0):
                raise ValueError("Bad superior error band, can't be lower than main")
            ax.errorbar(sim_df.index, sim_df['valor'], yerr=[sim_df["valor"] - sim_df[errorBand[0]], sim_df[errorBand[1]] - sim_df["valor"]], capsize=8)
        else:
            low_fmt = error_band_fmt[0] if type(error_band_fmt) in [tuple,list] else error_band_fmt
            up_fmt = error_band_fmt[1] if type(error_band_fmt) in [tuple,list] else error_band_fmt
            ax.plot(sim_df.index, sim_df[errorBand[0]],low_fmt,linewidth=0.5,alpha=0.75,label='_nolegend_',markersize=markersize)
            ax.plot(sim_df.index, sim_df[errorBand[1]],up_fmt,linewidth=0.5,alpha=0.75,label='_nolegend_',markersize=markersize)
            ax.fill_between(sim_df.index,sim_df[errorBand[0]], sim_df[errorBand[1]],alpha=0.1,label=errorBandLabel)
    # Lineas: 1 , 1.5 y 2 mts
    xmin=sim_df.index.min()
    xmax=sim_df.index.max()
    # Niveles alerta
    if thresholds.get("nivel_aguas_bajas"):
        logging.debug("Add threshold nivel_aguas_bajas: %.02f, xmin %s, xmax %s" % (thresholds["nivel_aguas_bajas"], xmin.isoformat(), xmax.isoformat()))
        plt.hlines(thresholds["nivel_aguas_bajas"], xmin, xmax, colors='orange', linestyles='-.', label='Aguas Bajas',linewidth=1.5)
    if thresholds.get("nivel_alerta"):
        plt.hlines(thresholds["nivel_alerta"], xmin, xmax, colors='y', linestyles='-.', label='Alerta',linewidth=1.5)
    if thresholds.get("nivel_evacuacion"):
        plt.hlines(thresholds["nivel_evacuacion"], xmin, xmax, colors='r', linestyles='-.', label='Evacuación',linewidth=1.5)
    # fecha emision
    if forecast_date is not None:
        if forecast_date.tzinfo is not None and forecast_date.tzinfo.utcoffset(forecast_date) is not None:
            ahora = forecast_date
        else:
            ahora = localtz.localize(forecast_date)
    elif not isinstance(obs_df, type(None)):
        ahora = obs_df.index.max()
    else: 
        ahora = localtz.localize(datetime.now())
    plt.axvline(x=ahora,color="black", linestyle="--",linewidth=2)#,label='Fecha de emisión')
    bbox = dict(boxstyle="round", fc="0.7")
    arrowprops = dict(
        arrowstyle="->",
        connectionstyle="angle,angleA=0,angleB=90,rad=10")
    offset = 10
    #xycoords='figure pixels',
    if annotate:
        xdisplay = ahora + relativedelta(days=1.0)
        ax.annotate(prono_annotation,
            xy=(xdisplay, ydisplay), xytext=(text_xoffset[0]*offset, -offset), textcoords='offset points',
            bbox=bbox, fontsize=18,
            color = prono_annotation_color)#arrowprops=arrowprops
        xdisplay = ahora - relativedelta(days=2)
        ax.annotate(obs_annotation,
            xy=(xdisplay, ydisplay), xytext=(text_xoffset[1]*offset, -offset), textcoords='offset points',
            bbox=bbox, fontsize=18)
        ax.annotate(forecast_date_annotation,
            xy=(ahora, ylim[0]+0.05*(ylim[1]-ylim[0])),fontsize=15, xytext=(ahora+relativedelta(days=0.3), ylim[0]+0.1*(ylim[1]-ylim[0])), arrowprops=dict(facecolor='black',shrink=0.05))
    if adjust_results_string is not None:
        plt.gcf().text(0.6, 0.85, adjust_results_string, fontsize=10)
    if footnote is not None:
        fig.subplots_adjust(bottom=footnote_height) # 0.2
        plt.figtext(0,0,footnote,fontsize=12,ha="left")
    if datum is not None and datum_template_string is not None:
        fig.subplots_adjust(bottom=footnote_height) # 0.2
        plt.figtext(0,0,datum_template_string % (station_name, str(round(datum+0.53,2)), str(round(datum,2))),fontsize=12,ha="left")
    if ylim:
        ax.set_ylim(ylim[0],ylim[1])
    if xlim is not None:
        xlim = list(xlim)
        if len(xlim) < 2:
            raise ValueError("xlim must be a 2-tuple")
        if xlim[0] is not None:
            xlim[0] = tryParseAndLocalizeDate(xlim[0])
        else:
            xlim[0] = xmin
        if xlim[1] is not None:
            xlim[1] = tryParseAndLocalizeDate(xlim[1])
        else:
            xlim[1] = xmax
    else:
        xlim = [xmin,xmax]
    xlim[0] = roundDownDate(xlim[0],relativedelta(days=1))
    xlim[1] = roundDownDate(xlim[1],relativedelta(days=1))
    ax.set_xlim(xlim[0],xlim[1])
    ax.tick_params(labeltop=False, labelright=True)
    plt.grid(True, which='both', color='0.75', linestyle='-.',linewidth=0.5)
    plt.tick_params(axis='both', labelsize=16)
    plt.xlabel(x_label, size=16)
    plt.ylabel(y_label, size=20)
    plt.legend(prop={'size':18},loc=2,ncol=1 )
    plt.title(title if title is not None else title_template_string % station_name,fontsize=20)
    #### TABLA
    if forecast_table:
        fig.subplots_adjust(right=0.8)
        h_resumen = [0,6,12,18]
        df_prono = sim_df[sim_df.index > ahora ].copy()
        df_prono['Hora'] = df_prono.index.hour
        df_prono['Dia'] = df_prono.index.day
        df_prono = df_prono[df_prono['Hora'].isin(h_resumen)].copy()
        df_prono = df_prono[df_prono['valor'].notnull()].copy()
        #print(df_prono)
        df_prono['Y_predic'] = df_prono['valor'].round(2)
        df_prono['Hora'] = df_prono['Hora'].astype(str)
        df_prono['Hora'] = df_prono['Hora'].replace('0', '00')
        df_prono['Hora'] = df_prono['Hora'].replace('6', '06')
        df_prono['Dia'] = df_prono['Dia'].astype(str)
        df_prono['Fechap'] = df_prono['Dia']+' '+df_prono['Hora']+'hrs'
        df_prono['Mes'] = df_prono.index.month.map('{:02d}'.format)
        df_prono["dd/mm hh"] = df_prono['Dia'] + "/" + df_prono['Mes'] + " " + df_prono['Hora']
        df_prono = df_prono.rename(columns={'Fechap':'Fecha','Y_predic':"Nivel"}) # df_prono[['Fechap','Y_predic',]]
        #print(df_prono)
        cell_text = []
        for row in range(len(df_prono)):
            cell_text.append(df_prono[table_columns].iloc[row])
            #print(cell_text)
        # columns = table_columns # ('Fecha','Nivel',)
        if len(cell_text):
            table = plt.table(cellText=cell_text,
                            colLabels=table_columns,
                            bbox = (1.08, 0, 0.2, 0.5))
            table.set_fontsize(12)
        else:
            logging.warn("No rows found for forecast table")
    #table.scale(2.5, 2.5)  # may help
    date_form = DateFormatter(date_form,tz=sim_df.index.tz) # "%H hrs \n %d-%b"
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_minor_locator(mdates.HourLocator(xaxis_minor_tick_hours)) # (3,9,15,21,)
    ## FRANJAS VERTICALES
    start_0hrs = sim_df.index.min().date()
    end_0hrs = (sim_df.index.max() + relativedelta(hours=12)).date()
    list0hrs = pandas.date_range(start_0hrs,end_0hrs)
    i = 1
    while i < len(list0hrs):
        ax.axvspan(list0hrs[i-1] + relativedelta(hours=3), list0hrs[i] + relativedelta(hours=3), alpha=0.1, color='grey')
        i=i+2
    plt.savefig(
        os.path.join(
            config["PYDRODELTA_DIR"],
            output_file
        ), 
        format = format
    )
    plt.close()

def getParamOrDefaultTo(param_name:str,value,param_set:dict,default=None):
    if value is not None:
        return value
    elif param_set is not None and param_name in param_set:
        return param_set[param_name]
    else:
        return default

def readCsvFile(csv_file):
    if not os.path.exists(csv_file):
        raise Exception("csv file %s not found" % csv_file)
    with open(csv_file, newline='') as csvfile:
        return [row for row in csv.DictReader(csvfile)]

def parseObservations(observations:list) -> list:
    result = []
    for i, o in enumerate(observations):
        # option 1: dict { "timestart": str, "valor": number }
        if type(o) == dict:
            if "timestart" not in o:
                raise Exception("timestart missing from observations item %i" % i)
            result.append({
                "timestart": tryParseAndLocalizeDate(o["timestart"]),
                "valor": float(o["valor"]) if "valor" in o and o["valor"] is not None else None
            })
        # option 2: list
        elif type(o) == list or type(o) == tuple:
            if len(o) == 0:
                continue
            result.append({
                "timestart": tryParseAndLocalizeDate(o[0]),
                "valor": float(o[1]) if len(o) > 1 and o[1] is not None else None
            })
    return result

def readDataFromCsvFile(csv_file: str,series_id: int,timestart=None,timeend=None) -> list:
    """reads from csv_file and returns list of observaciones (dicts). series_id must be in the header of the column containing the values of the corresponding series. timestart column must be in iso format. Other columns are ignored"""
    observaciones = readCsvFile(csv_file)
    data = []
    for o in observaciones:
        parsed_timestart = tryParseAndLocalizeDate(o["timestart"])
        if timestart is not None and parsed_timestart < timestart:
            continue
        if timeend is not None and parsed_timestart > timeend:
            continue
        if str(series_id) in o:
            parsed_valor = tryParseFloat(o[str(series_id)])
            data.append({"series_id": series_id, "timestart": parsed_timestart, "valor": parsed_valor})      
        elif "valor" in o:
            parsed_valor = tryParseFloat(o["valor"])
            data.append({"series_id": series_id, "timestart": parsed_timestart, "valor": parsed_valor})
        else:
            raise Exception("column %s missing from csv file %s." % (series_id,csv_file))
    return data

def tryParseFloat(value,allow_none=True):
    if type(value) == str:
        if len(value):
            try:
                parsed_float = float(value)
            except ValueError:
                raise(ValueError)
        elif allow_none:
            parsed_float = None
        else:
            raise(ValueError("Invalid float: empty string"))
    else:
        try:
            parsed_float = float(value)
        except ValueError:
            raise(ValueError)
    return parsed_float

def ParseApiConfig(api_config = None):
    if api_config is not None:
        pars = api_config.split("@")
        if len(pars) < 2:
            raise ValueError("Invalid string. Valid sintax is: token@url")
        return {
            "url": pars[1],
            "token": pars[0]
        }
    else:
        return None

def groupByCalibrationPeriod(
    data : pandas.DataFrame,
    calibration_period : Tuple[datetime, datetime]
) -> Tuple[pandas.DataFrame, pandas.DataFrame]:
    """Split data between calibration and validation periods
    
    Args:
        data : pandas.DataFrame
            Series DataFrame to split
        calibration_period : Tuple[datetime, datetime]
            Begin and end dates of calibration period
    
    Returns:
        Tuple[pandas.DataFrame, pandas.DataFrame] : calibration data (or None if data not  found), validation data (or None if data not  found)."""
    grouped_by_date = data.groupby((data.index >= calibration_period[0]) & (data.index <= calibration_period[1]))
    val = None
    cal = None
    for k, df in grouped_by_date:
        if k == True:
            cal = df
        else:
            val = df
    return cal, val

def coalesce(*args):
    return next((item for item in args if item is not None), None)

colormap = plt.colormaps["hsv"]
def getRandColor():
    return colormap(random.randrange(colormap.N))

def first(l : list) -> any:
    return l[0] if len(l) else np.nan

def last(l : list) -> any:
    return l[len(l)-1] if len(l) else np.nan

def mad(l : list) -> float:
    mean = np.mean(l)
    return np.mean([abs(x - mean) for x in l])

def filter_func(ind, base : datetime, dt: relativedelta):
    return ind >= base and ind < base + dt

def getRowsWithinTimestep(data : DataFrame, base : datetime, dt : relativedelta) -> DataFrame:
    return data.loc[map(filter_func, data.index, [base for x in data.index], [dt for x in data.index])]

def aggregateValuesWithinTimestep(data : DataFrame, base : datetime, dt : relativedelta, column: str = "valor", pass_nan : bool = True, agg_func : str = "sum") -> float:
    valid_agg_func = {
        "sum": np.sum,
        "first": first,
        "last": last,
        "mean": np.mean,
        "median": np.median,
        "min": min,
        "max": max,
        "std": np.std,
        "var": np.var,
        "prod": np.prod,
        "mad": mad
    }
    if agg_func not in valid_agg_func.keys():
        raise ValueError("Invalid agg_func")
    rows = getRowsWithinTimestep(data, base, dt)
    if pass_nan and not len(rows["valor"]):
        return np.nan  
    return valid_agg_func[agg_func](rows[column])

def aggregateByTimestep(data : DataFrame, index : DatetimeIndex, dt : relativedelta, column: str = "valor", pass_nan : bool = True, agg_func : str = "sum") -> Series:
    """For each timestamp in index, return aggregate function agg_func column column of matching rows of data. data.index must be a DatetimeIndex. For a given index item i, matching rows are those where row index is greater than or equal to i and lower than i + dt

    Args:
        data (DataFrame): the unaggregated data
        index (DatetimeIndex): index of output Series
        dt (timedelta): time support of output Series
        column (str, optional): Column name of data to aggregate. Defaults to "valor".
        pass_nan (bool, optional): If no rows are matched return NaN. Defaults to True. If False, depending on agg_func, it may return 0
        agg_func (str, optional): Aggregation function. Defaults to "sum".
        Valid values:
          - sum (default)
          - first
          - last
          - mean
          - median
          - min
          - max
          - std
          - var
          - prod
          - mad

    Returns:
        Series: the aggregated series. Series of type float with index of type DatetimeIndex
    """
    return Series([aggregateValuesWithinTimestep(data, i, dt, column, pass_nan, agg_func) for i in index], index)

def relativedeltaToSeconds(rd : relativedelta):
    if not isinstance(rd, relativedelta):
        raise TypeError("Value must be of type relativedelta")
    now = datetime.now()
    future = now + rd
    delta = future - now
    return delta.total_seconds()

def compare_durations(d1 : Union[relativedelta,timedelta], d2 : Union[relativedelta,timedelta],operation:Literal["gt","lt","ge","le","e"]="gt"):
    d1_seconds = relativedeltaToSeconds(d1) if isinstance(d1,relativedelta) else d1.total_seconds()
    d2_seconds = relativedeltaToSeconds(d2) if isinstance(d2,relativedelta) else d2.total_seconds()
    if operation == "gt":
        return d1_seconds > d2_seconds
    elif operation == "lt":
        return d1_seconds < d2_seconds
    elif operation == "ge":
        return d1_seconds >= d2_seconds
    elif operation == "le":
        return d1_seconds <= d2_seconds
    elif operation == "e":
        return d1_seconds == d2_seconds
    else:
        raise ValueError("Invalid operation. Valid values: gt, lt, ge, le, e")

def timedelta_to_relativedelta(td: timedelta) -> relativedelta:
    total_seconds = td.total_seconds()
    
    days, remainder = divmod(total_seconds, 86400)  # seconds in a day
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return relativedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds)
    )

def relativedelta_to_timedelta(rd: relativedelta) -> timedelta:
    if not isinstance(rd, relativedelta):
        raise TypeError("Value must be of type relativedelta")
    total_seconds = relativedeltaToSeconds(rd)
    days, remainder = divmod(total_seconds, 86400)  # seconds in a day
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return timedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds)
    )

def multiply_relativedelta(rd: relativedelta, n: int) -> relativedelta:
    return relativedelta(
        years=rd.years * n,
        months=rd.months * n,
        days=rd.days * n,
        hours=rd.hours * n,
        minutes=rd.minutes * n,
        seconds=rd.seconds * n,
        microseconds=rd.microseconds * n,
        weeks=rd.weeks * n
    )

def interpolate_or_copy_closest(data : Series,interpolation_limit : timedelta) -> Series:

    # Forward and backward fills
    ffill = data.ffill(limit=None)
    bfill = data.bfill(limit=None)

    # Timestamps of fills
    ffill_times = data.index.to_series().where(data.notna()).ffill()
    bfill_times = data.index.to_series().where(data.notna()).bfill()

    # Time differences between original and fill
    delta_fwd = data.index.to_series() - ffill_times
    delta_bwd = bfill_times - data.index.to_series()

    # Mask values where gap is too big
    use_ffill = (delta_fwd <= interpolation_limit)
    use_bfill = (delta_bwd <= interpolation_limit)

    # Choose closest direction when both are valid
    filled = data.copy()
    for i in data[data.isna()].index:
        if use_ffill[i] and use_bfill[i]:
            # interpolate
            filled[i] = (ffill[i] * delta_fwd[i] + bfill[i] * delta_bwd[i]) / (delta_fwd[i] + delta_bwd[i])
        elif use_ffill[i]:
            filled[i] = ffill[i]
        elif use_bfill[i]:
            filled[i] = bfill[i]
        # else: leave as NaN (too far from both sides)

    return filled
