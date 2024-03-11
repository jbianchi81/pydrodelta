import dateutil.parser
import dateutil.relativedelta
import pytz
localtz = pytz.timezone('America/Argentina/Buenos_Aires')
import pandas
from datetime import timedelta, datetime
import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import logging
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
import csv
import os.path
from typing import Union

def interval2timedelta(interval : Union[dict,float,timedelta]):
    """Parses duration dict or number of days into datetime.timedelta object
    
    Parameters:
    -----------
    interval : dict or float (decimal number of days) or datetime.timedelta
        If dict, allowed keys are:
        - days
        - seconds
        - microseconds
        - minutes
        - hours
        - weeks
    
    Returns:
    --------
    duration : datetime.timedelta

    Examples:

    ```
    interval2timedelta({"hours":1, "minutes": 30})
    interval2timedelta(1.5/24)
    ```
    """
    if isinstance(interval,timedelta):
        return interval
    if isinstance(interval,(float,int)):
        return timedelta(days=interval)
    days = 0
    seconds = 0
    microseconds = 0
    milliseconds = 0
    minutes = 0
    hours = 0
    weeks = 0
    for k in interval:
        if k == "milliseconds" or k == "millisecond":
            milliseconds = interval[k]
        elif k == "seconds" or k == "second":
            seconds = interval[k]
        elif k == "minutes" or k == "minute":
            minutes = interval[k]
        elif k == "hours" or k == "hour":
            hours = interval[k]
        elif k == "days" or k == "day":
            days = interval[k]
        elif k == "weeks" or k == "week":
            weeks = interval[k] * 86400 * 7
    return timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

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
        date_string : Union[str,float,datetime],
        timezone : str='America/Argentina/Buenos_Aires'
    ) -> datetime:
    """
    Datetime parser. If duration is provided, computes date relative to now.

    Parameters:
    -----------
    date_string : str or float or datetime.datetime
        For absolute date: ISO-8601 datetime string or datetime.datetime.
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
    ```
    """
    
    date = dateutil.parser.isoparse(date_string) if isinstance(date_string,str) else date_string
    is_from_interval = False
    if isinstance(date,dict):
        date = datetime.now() + dateutil.relativedelta.relativedelta(**date)
        is_from_interval = True
    elif isinstance(date,(int,float)):
        date = datetime.now() + dateutil.relativedelta.relativedelta(days=date)
        is_from_interval = True
    if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
        try:
            date = pytz.timezone(timezone).localize(date)
        except pytz.exceptions.NonExistentTimeError:
            logging.warning("NonexistentTimeError: %s" % str(date))
            return None
    else:
        date = date.astimezone(pytz.timezone(timezone))
    return date # , is_from_interval

def roundDownDate(date : datetime,timeInterval : timedelta,timeOffset : timedelta=None) -> datetime:
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

def roundDate(date : datetime,timeInterval : timedelta,timeOffset : timedelta=None, to="up") -> datetime:
    date_0 = tryParseAndLocalizeDate(datetime.combine(date.date(),datetime.min.time()))
    if timeOffset is not None:
        date_0 = date_0 + timeOffset 
    while date_0 < date:
        date_0 = date_0 + timeInterval
    if to == "up":
        return date_0
    else:
        return date_0 - timeInterval

def createDatetimeSequence(
    datetime_index : pandas.DatetimeIndex=None, 
    timeInterval  = timedelta(days=1), 
    timestart = None, 
    timeend = None, 
    timeOffset = None
    ) -> pandas.DatetimeIndex:
    #Fechas desde timestart a timeend con un paso de timeInterval
    #data: dataframe con index tipo datetime64[ns, America/Argentina/Buenos_Aires]
    #timeOffset sólo para timeInterval n days
    if datetime_index is None and (timestart is None or timeend is None):
        raise Exception("Missing datetime_index or timestart+timeend")
    timestart = timestart if timestart is not None else datetime_index.min()
    timestart = roundDate(timestart,timeInterval,timeOffset,"up")
    timeend = timeend if timeend  is not None else datetime_index.max()
    timeend = roundDate(timeend,timeInterval,timeOffset,"down")
    return pandas.date_range(start=timestart, end=timeend, freq=pandas.DateOffset(days=timeInterval.days, hours=timeInterval.seconds // 3600, minutes = (timeInterval.seconds // 60) % 60))

def f1(row,column="valor",timedelta_threshold=None):
    if -row["diff_with_next"] > timedelta_threshold:
        return row[column]
    else:
        return row["interpolated_backward"]

def f2(row,column="valor",timedelta_threshold=None):
    if row["diff_with_previous"] > timedelta_threshold:
        return row[column]
    else:
        return row["interpolated_forward"]

def f3(row,column="valor",timedelta_threshold=None):
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
    time_interval : timedelta, 
    timestart = None, 
    timeend = None, 
    time_offset = None, 
    column = "valor", 
    interpolate = True, 
    interpolation_limit = 1,
    tag_column = None, 
    extrapolate = False
    ) -> pandas.DataFrame:
    """
    genera serie regular y rellena nulos interpolando
    if interpolate=False, interpolates only to the closest timestep of the regular timeseries. If observation is equidistant to preceding and following timesteps it interpolates to both.
    """
    df_regular = pandas.DataFrame(index = createDatetimeSequence(data.index, time_interval, timestart, timeend, time_offset))
    df_regular.index.rename('timestart', inplace=True)
    if not len(data):
        df_regular[column] = None
        if tag_column is not None:
            df_regular[tag_column] = None
        return df_regular
    df_join = df_regular.join(data, how = 'outer')
    if interpolate:
        # Interpola
        min_obs_date, max_obs_date = (df_join[~pandas.isna(df_join[column])].index.min(),df_join[~pandas.isna(df_join[column])].index.max())
        df_join["interpolated"] = df_join[column].interpolate(method='time',limit=interpolation_limit,limit_direction='both',limit_area=None if extrapolate else 'inside')
        if tag_column is not None:
            # print("columns: " + df_join.columns)
            df_join[tag_column] = [x[tag_column] if pandas.isna(x["interpolated"]) else "extrapolated" if i < min_obs_date or i > max_obs_date else "interpolated" if pandas.isna(x[column]) else x[tag_column] for (i, x) in df_join.iterrows()]
        df_join[column] = df_join["interpolated"]
        del df_join["interpolated"]
        df_regular = df_regular.join(df_join, how = 'left')
    else:
        timedelta_threshold = time_interval / 2 # takes half time interval as maximum time distance for interpolation
        df_join = df_join.reset_index()
        df_join["diff_with_previous"] = df_join["timestart"].diff()
        df_join["diff_with_next"] = df_join["timestart"].diff(periods=-1)
        df_join = df_join.set_index("timestart")
        df_join["interpolated_backward"] = df_join[column].interpolate(method='time',limit=1,limit_direction='backward',limit_area=None)
        df_join["interpolated_forward"] = df_join[column].interpolate(method='time',limit=1,limit_direction='forward',limit_area=None)
        df_join["interpolated_backward_filtered"] = df_join.apply(lambda row: f1(row,column,timedelta_threshold),axis=1) #[ x[column] if -x["diff_with_next"] > timedelta_threshold else x.interpolated_backward for (i,x) in df_join.iterrows()]
        df_join["interpolated_forward_filtered"] = df_join.apply(lambda row: f2(row,column,timedelta_threshold),axis=1)#[ x[column] if x["diff_with_previous"] > timedelta_threshold else x.interpolated_forward for (i,x) in df_join.iterrows()]
        df_join["interpolated_final"] = df_join.apply(lambda row: f3(row,column,timedelta_threshold),axis=1) #[x.interpolated_backward_filtered if pandas.isna(x.interpolated_forward_filtered) else x.interpolated_forward_filtered for (i,x) in df_join.iterrows()]
        if tag_column is not None:
            df_join["new_tag"] = df_join.apply(lambda row: f4(row,column,tag_column),axis=1) #[x[tag_column] if pandas.isna(x.interpolated_final) else "interpolated" if pandas.isna(x.valor) else x[tag_column] for (i,x) in df_join.iterrows()]
            df_regular = df_regular.join(df_join[["interpolated_final","new_tag"]].rename(columns={"interpolated_final":column,"new_tag":tag_column}), how = 'left')
        else:
            df_regular = df_regular.join(df_join[["interpolated_final",]].rename(columns={"interpolated_final":column}), how = 'left')
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

def interpolateData(data,column="valor",tag_column=None,interpolation_limit=1,extrapolate=False):
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
    offset : timedelta,
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

def adjustSeries(sim_df,truth_df,method="lfit",plot=True,return_adjusted_series=True,tag_column=None,title=None)  -> pandas.Series:
    if method == "lfit":
        data = truth_df.join(sim_df,how="left",rsuffix="_sim")
        lr, quant_Err, r2, coef, intercept =  ModelRL(data,"valor",["valor_sim"])
        # logging.info(quant_Err)
        # Prediccion
        aux_df = sim_df.copy().dropna()
        predict = lr.predict(aux_df[["valor"]].values)
        aux_df["adj"] = predict
        aux_df = aux_df.rename(columns={"valor":"valor_sim","tag":"tag_sim"}).join(truth_df.rename(columns={"valor":"valor_obs","tag":"tag_obs"}),how='outer')
        if plot:
            plt.figure(figsize=(16,8))
            plt.plot(aux_df[["valor_obs","valor_sim","adj"]]) # (data)
            plt.legend(["valor_obs","valor_sim","adj"]) # data.columns)
            if title:
                plt.title(title)
            plt.figtext(0.5, 0.01, "r2: %.04f, coef: %s, intercept: %.04f" % (r2,",".join(["%.04f" % x for x in coef]), intercept))
        if return_adjusted_series:
            if tag_column is not None:
                aux_df["tag_adj"] = [None if pandas.isna(x) else "%s,adjusted" % x for x in aux_df["tag_sim"]]
                return (aux_df["adj"], aux_df["tag_adj"],{"lr": lr, "quant_Err": quant_Err, "r2": r2, "coef": coef, "intercept": intercept})
            else:
                return (aux_df["adj"], None, {"lr": lr, "quant_Err": quant_Err, "r2": r2, "coef": coef, "intercept": intercept})
        else:
            return {"lr": lr, "quant_Err": quant_Err, "r2": r2, "coef": coef, "intercept": intercept}
    else:
        raise Exception("unknown method " + method)

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
    # The coefficients
    # The mean squared error
    mse = mean_squared_error(Y_test, Y_predictions)
    # The coefficient of determination: 1 is perfect prediction
    coefDet = r2_score(Y_test, Y_predictions)
    logging.debug('Coefficients B0: %.5f, coefficients: %.5f, Mean squared error: %.5f, r2_score: %.5f' % (lr.intercept_, lr.coef_, mse, coefDet))
    train['Error_pred'] =  train['Y_predictions']  - train[var_obj]
    quant_Err = train['Error_pred'].quantile([.001,.05,.95,.999])
    return lr,quant_Err,r2,coef,intercept
    
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
    datum:float=0,
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
    xlim:tuple=None
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
    datum = 0 if datum is None else datum
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
    ax.plot(sim_df.index, sim_df['valor'], '-',color='b',label=prono_label,linewidth=3)
    if not isinstance(obs_df, type(None)):
        ax.plot(obs_df.index, obs_df['valor'],'o',color='k',label=obs_label,linewidth=3)
        if obsLine:
            ax.plot(obs_df.index, obs_df['valor'],'-',color='k',linewidth=1,markersize=markersize)
    if not isinstance(extraObs,type(None)):
        extraObs.index = extraObs.index.tz_convert(tz)
        ax.plot(extraObs.index, extraObs['valor'],'o',color='grey',label=extraObsLabel,linewidth=3,alpha=0.5)
        ax.plot(extraObs.index, extraObs['valor'],'-',color='grey',linewidth=1,alpha=0.5)
    if errorBand is not None:
        ax.plot(sim_df.index, sim_df[errorBand[0]],'-',color='k',linewidth=0.5,alpha=0.75,label='_nolegend_')
        ax.plot(sim_df.index, sim_df[errorBand[1]],'-',color='k',linewidth=0.5,alpha=0.75,label='_nolegend_')
        ax.fill_between(sim_df.index,sim_df[errorBand[0]], sim_df[errorBand[1]],alpha=0.1,label=errorBandLabel)
    # Lineas: 1 , 1.5 y 2 mts
    xmin=sim_df.index.min()
    xmax=sim_df.index.max()
    # Niveles alerta
    if thresholds.get("aguas_bajas"):
        plt.hlines(thresholds["aguas_bajas"], xmin, xmax, colors='y', linestyles='-.', label='Aguas Bajas',linewidth=1.5)
    if thresholds.get("alerta"):
        plt.hlines(thresholds["alerta"], xmin, xmax, colors='y', linestyles='-.', label='Alerta',linewidth=1.5)
    if thresholds.get("evacuacion"):
        plt.hlines(thresholds["evacuacion"], xmin, xmax, colors='r', linestyles='-.', label='Evacuación',linewidth=1.5)
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
    xdisplay = ahora + timedelta(days=1.0)
    ax.annotate(prono_annotation,
        xy=(xdisplay, ydisplay), xytext=(text_xoffset[0]*offset, -offset), textcoords='offset points',
        bbox=bbox, fontsize=18)#arrowprops=arrowprops
    xdisplay = ahora - timedelta(days=2)
    ax.annotate(obs_annotation,
        xy=(xdisplay, ydisplay), xytext=(text_xoffset[1]*offset, -offset), textcoords='offset points',
        bbox=bbox, fontsize=18)
    ax.annotate(forecast_date_annotation,
        xy=(ahora, ylim[0]+0.05*(ylim[1]-ylim[0])),fontsize=15, xytext=(ahora+timedelta(days=0.3), ylim[0]+0.1*(ylim[1]-ylim[0])), arrowprops=dict(facecolor='black',shrink=0.05))
    fig.subplots_adjust(bottom=0.2,right=0.8)
    if footnote is not None:
        plt.figtext(0,0,footnote,fontsize=12,ha="left")
    if datum is not None and datum_template_string is not None:
        plt.figtext(0,0,datum_template_string % (station_name, str(round(datum+0.53,2)), str(round(datum,2))),fontsize=12,ha="left")
    if ylim:
        ax.set_ylim(ylim[0],ylim[1])
    if xlim is not None:
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
    xlim[0] = roundDownDate(xlim[0],timedelta(days=1))
    xlim[1] = roundDownDate(xlim[1],timedelta(days=1))
    ax.set_xlim(xlim[0],xlim[1])
    ax.tick_params(labeltop=False, labelright=True)
    plt.grid(True, which='both', color='0.75', linestyle='-.',linewidth=0.5)
    plt.tick_params(axis='both', labelsize=16)
    plt.xlabel(x_label, size=16)
    plt.ylabel(y_label, size=20)
    plt.legend(prop={'size':18},loc=2,ncol=1 )
    plt.title(title if title is not None else title_template_string % station_name,fontsize=20)
    #### TABLA
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
    df_prono = df_prono[['Fechap','Y_predic',]]
    #print(df_prono)
    cell_text = []
    for row in range(len(df_prono)):
        cell_text.append(df_prono.iloc[row])
        #print(cell_text)
    columns = ('Fecha','Nivel',)
    table = plt.table(cellText=cell_text,
                      colLabels=columns,
                      bbox = (1.08, 0, 0.2, 0.5))
    table.set_fontsize(12)
    #table.scale(2.5, 2.5)  # may help
    date_form = DateFormatter("%H hrs \n %d-%b",tz=sim_df.index.tz)
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_minor_locator(mdates.HourLocator((3,9,15,21,)))
    ## FRANJAS VERTICALES
    start_0hrs = sim_df.index.min().date()
    end_0hrs = (sim_df.index.max() + timedelta(hours=12)).date()
    list0hrs = pandas.date_range(start_0hrs,end_0hrs)
    i = 1
    while i < len(list0hrs):
        ax.axvspan(list0hrs[i-1] + timedelta(hours=3), list0hrs[i] + timedelta(hours=3), alpha=0.1, color='grey')
        i=i+2
    plt.savefig(output_file, format='png')
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
        if str(series_id) not in o:
            raise Exception("column %s missing from csv file %s." % (series_id,csv_file))
        parsed_valor = tryParseFloat(o[str(series_id)])
        data.append({"series_id": series_id, "timestart": parsed_timestart, "valor": parsed_valor})
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
