from pandas import DataFrame
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt
import numpy as np
import logging
from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from pydrodelta.util import tryParseAndLocalizeDate
from typing import Union, List, Tuple
from pandas import DataFrame, concat, DatetimeIndex
from matplotlib import pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pydrodelta.descriptors.dataframe_descriptor import DataFrameDescriptor
from pydrodelta.descriptors.float_descriptor import FloatDescriptor
from pydrodelta.procedures.analogy import CreaVariablesTemporales, month2Date

class PersistenceProcedureFunction(ProcedureFunction):
    """Persistence forecast procedure"""

    _boundaries = [
        FunctionBoundary({"name": "input", "optional": True})
    ]

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]

    @property
    def search_length(self) -> int:
        """search_length : longitud de la serie para buscar Analogas"""
        return int(self.parameters["search_length"]) if "search_length" in self.parameters else 6

    @property
    def forecast_length(self) -> int:
        """forecast_length : longitud del pronostico"""
        return int(self.parameters["forecast_length"]) if "forecast_length" in self.parameters else 4 
    
    @property
    def time_window(self) -> int:
        """Ventana temporal"""
        return self.parameters["time_window"] if "time_window" in self.parameters else "month"

    @property
    def parameters_with_defaults(self) -> dict:
        return {
            "search_.ength": self.search_length,
            "forecast_length": self.forecast_length,
            "time_window": self.time_window
        }

    @property
    def skip_first_years(self) -> int:
        return self.extra_pars.get("skip_first_years") if "skip_first_years" in self.extra_pars else 2

    errores = DataFrameDescriptor()

    df_prono = DataFrameDescriptor()

    data = DataFrameDescriptor()

    error_stats = DataFrameDescriptor()

    percentil = FloatDescriptor()

    def __init__(
        self,
        parameters : dict,
        **kwargs
        ):
        """_summary_

        Arguments:
        ----------
        parameters (dict): Model parameters
            
            Properties:
                - search_length : int = 6
                    longitud de periodo de busqueda
                - forecast_length : int = 4
                    longitud del pronostico
                - time_window : "year" | "month" | "day" | "yrDay" | "wkDay" = "month"
                    Ventana temporal

        extra_pars : dict
        
            Properties:
            - add_error_band : bool = False
            - skip_first_years : int = 2
            - only_last_years : int = None - not used
            - vent_resamp_range : Tuple[int,int] = None - not used
        
        **kwargs : see ..procedure_function.ProcedureFunction
        """
        super().__init__(parameters = parameters, **kwargs)
        getSchemaAndValidate(dict(kwargs, type = "Persistence", parameters = parameters),"PersistenceProcedureFunction")
        self.errores = None
        self.df_prono = None
        self.data = None
        self.error_stats = None
        self.percentil = None

    def run(
        self,
        input : List[DataFrame] = None,
        forecast_date : datetime = None,
        save_results : str = None,
        add_error_band : bool = None,
        skip_first_years : int = None, 
        only_last_years : int = None, 
        vent_resamp_range : Tuple[int,int] = None,
        error_forecast_date_window : int = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Parameters:
        -----------
        input : list of DataFrames
            Boundary conditions. If None, runs .loadInput
        
        forecast_date : datetime = None
            forecast date. Defaults to forecast_date of plan

        Returns:
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if forecast_date is not None:
            forecast_date = tryParseAndLocalizeDate(forecast_date)
        elif self.forecast_date is None:
            raise ValueError("Missing forecast_date")
        else:
            forecast_date = self.forecast_date

        if save_results is None:
            save_results = self.save_results
        
        add_error_band = add_error_band if add_error_band is not None else self.extra_pars.get("add_error_band")
        skip_first_years = skip_first_years if skip_first_years is not None else self.skip_first_years
        # only_last_years = only_last_years if only_last_years is not None else self.only_last_years
        # vent_resamp_range = vent_resamp_range if vent_resamp_range is not None else self.vent_resamp_range
        # error_forecast_date_window = error_forecast_date_window if error_forecast_date_window is not None else self.error_forecast_date_window

        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)
        
        if not isinstance(input,list):
            raise ValueError("Input must be a list of DataFrame")
        if not len(input):
            raise ValueError("Input is of null length. Must be of length 1 [DataFrame]")
        if not isinstance(input[0],DataFrame):
            raise ValueError("Input[0] must be of type DataFrame")
        if not isinstance(input[0].index, DatetimeIndex):
            raise ValueError("Input[0].index must be of type DatetimeIndex")
        if "valor" not in input[0].columns:
            raise ValueError("'valor' column missing from input[0]")

        if forecast_date.day > 27:
            mes_select = forecast_date.month
            yr_select = forecast_date.year
        else:
            if forecast_date.month == 1:
                mes_select = 12
                yr_select = forecast_date.year - 1
            else:
                mes_select = forecast_date.month - 1
                yr_select = forecast_date.year

        self.data = input[0].copy()
        CreaVariablesTemporales(self.data)

        ### Metodo Persistencia.

        self.df_prono, self.percentil = MetodoPersistencia(
            self.data,
            "valor",
            mes_select,
            yr_select,
            self.search_length, 
            self.forecast_length,
            self.time_window,
            Prono=True)
                
        # Mes a formato fecha
        self.df_prono['month'] = self.df_prono.apply(lambda x: month2Date(x.year, x.month), axis=1)
        # crea columna mes_ant
        self.df_prono["mes_ant"] = range(1,len(self.df_prono) + 1,1)
        
        if add_error_band:
            ## 2 - Calcula errores X serie
            # if vent_resamp_range is None and error_forecast_date_window is not None:
            #     # set forecast date window for seasonsized error
            #     steps = range(1,53 if self.time_window == "week" else 13,1)
            #     vent_resamp_range = (steps[(forecast_date.month - error_forecast_date_window - 1) % len(steps)],steps[(forecast_date.month + error_forecast_date_window - 1)  % len(steps)])
            self.errores = ErrorXPersistencia(
                self.boundaries[0].node_id,
                self.data,
                "valor",
                self.search_length,
                self.forecast_length,
                self.time_window,
                skip_first_years=skip_first_years,
                plot=False) # connBBDD=conn

            column = 0
            self.error_stats = DataFrame(columns = ["mes_ant","count","mean","std"])
            for i, row in self.df_prono.iterrows():
                if column > self.forecast_length - 1:
                    break
                self.error_stats.loc[len(self.error_stats)] = [
                    row["mes_ant"],
                    self.errores.iloc[:,column].dropna().count(),
                    self.errores.iloc[:,column].mean(),
                    self.errores.iloc[:,column].std()
                ]
                column = column + 1
            # merge stats a df_prono
            self.df_prono = self.df_prono.merge(self.error_stats,on="mes_ant",how="left")
            # set uncertainty band
            self.df_prono["inferior"] = self.df_prono["VarProno"] - 1.645 * self.df_prono["std"]
            self.df_prono["superior"] = self.df_prono["VarProno"] + 1.645 * self.df_prono["std"]

            output = self.df_prono[['month','VarProno','inferior','superior']].rename(columns={"month":"timestart", "VarProno":"valor"}).set_index("timestart")
        
        else:
            output = self.df_prono[['month','VarProno']].rename(columns={"month":"timestart", "VarProno":"valor"}).set_index("timestart")

        return (
            [output], 
            ProcedureFunctionResults(
                data = self.df_prono,
                parameters = self.parameters
            )
        )
    


def MetodoPersistencia( data : DataFrame,
                        var : str,
                        mes : int,
                        year : int,
                        longBusqueda : int,
                        longProno : int,
                        vent_resamp : str = "month",
                        Prono=True,
                        Plot=False):
    """
    Método persistencia

    Parameters:
    -----------
    df_full :       Df con columna de fecha-variable

    var :           Nombre de la variable

    mes:            mes seleccionado

    year:           year seleccionado

    longBusqueda:   long serie hacia atrás

    longProno:      longitud del prono

    vent_resamp:    Ventana temporal del resampleo

    Prono=True

    Plot=False
    """
    
    # Busca la fecha seleccionada
    fecha_Obj = data.query("year=="+str(year)+" and "+vent_resamp+"=="+str(mes))
    if not len(fecha_Obj):
        raise ValueError("Objective timestamp for year %i, %s %i not found" % (year, vent_resamp, mes))
    
    # Toma el id de la fecha seleccionada
    idx_select = fecha_Obj.index[0].to_pydatetime()

    # Toma el caudal de esta fecha
    value_select = fecha_Obj[var].values[0]
    if np.isnan(value_select):
        raise ValueError("Invalid value: nan at timestamp %s" % idx_select)

    # Calcula el cuantil de ese caudal para el mes correspondiente.
    df_Base = data[:idx_select].copy()   # Filtra datos posteriores a la fecha seleccionada
    ultimo_quantil = getQuantile(df_Base, mes, value_select, vent_resamp, var)
    if ultimo_quantil < 0 or ultimo_quantil > 1:
        raise Exception("Cuantil inválido: %s" % str(ultimo_quantil))
    #print(fecha_Obj)
    #print('Cuantil cero: ',ultimo_quantil)

    # Index para armar el Df de datos Obs para la fecha seleccionada
    idx_fecha_fin = idx_select
    idx_fecha_fin_prono = idx_fecha_fin + relativedelta(months=longProno)
    
    if Prono:
        idx_fecha_inicio = idx_fecha_fin - relativedelta(months=longBusqueda)
        # Arma el Df de datos Obs para la fecha seleccionada
        dfObj = data[idx_fecha_inicio:idx_fecha_fin].copy()
        dfObj = dfObj[[vent_resamp,var]]
        dfObj = dfObj.rename(columns={var:year})

        # Arma el Df para el prono. Fecha Selecionada + dias prono
        
        index_i = []
        idx_select = idx_select + relativedelta(months=1)
        while idx_select <= idx_fecha_fin_prono:
            index_i.append(idx_select)
            idx_select = idx_select + relativedelta(months=1)
        # index_i = range(idx_fecha_fin, idx_fecha_fin_prono, 1)
        dfProno = DataFrame(index = index_i,columns=['id',vent_resamp,'VarProno'])
        dfProno[vent_resamp] = range(mes+1, mes+1+longProno, 1)
        
        ### Solo para vent_resamp='month' ####
        dfProno['id']= "%s%s" % (str(year),str(mes))
        dfProno['year']= year
        dfProno.loc[dfProno[vent_resamp]  > 12, 'year'] = dfProno.loc[dfProno[vent_resamp]  > 12, 'year'] + 1
        dfProno.loc[dfProno[vent_resamp]  > 12, vent_resamp] = dfProno.loc[dfProno[vent_resamp]  > 12, vent_resamp] - 12

        # Agrega el Q pronosticado.
        # Con el cuantil obtenido busca el caudales en los meses siguientes
        for index, row in dfProno.iterrows():
            mes_i = int(row[vent_resamp])
            Q_next_month = getValueOfQuantile(df_Base, mes_i, ultimo_quantil, vent_resamp, var)
            dfProno.loc[index,'VarProno'] = Q_next_month

            # df_mes_i = df_full.loc[df_full[vent_resamp] == mes_i,var]
            # sns.boxplot(y=df_mes_i)
            # plt.title(mes_i)
            # plt.show()
            # plt.close()

        # Arma BoxPlot
        if Plot:
            FiguraSerieBoxPlot("Estacion",dfObj,year,dfProno,'VarProno',data,vent_resamp,var,longBusqueda)
        return dfProno, ultimo_quantil
        
    # Para el Cálculo del error (hindcast)
    else:
        # Arma el Df para el prono. Fecha Selecionada + dias prono
        dfProno = data[idx_fecha_fin:idx_fecha_fin_prono].copy().reset_index()
        dfProno = dfProno[[vent_resamp,var]]
        dfProno = dfProno.rename(columns={var:var+'_Obs'})
        dfProno[var+'_Prono'] = np.nan
        
        # Agrega el Q pronosticado. 
        # Con el cuantil obtenido busca el caudales en los meses siguientes
        for index, row in dfProno.iterrows():
            mes_i = int(row[vent_resamp])
            Q_next_month = getValueOfQuantile(df_Base, mes_i, ultimo_quantil, vent_resamp, var)
            dfProno.loc[index,var+'_Prono']=Q_next_month
        # Devuelve el Df Con el Prono  
        return dfProno, ultimo_quantil

def FiguraSerieBoxPlot(nomEst,df_obs,v_obs,df_sim,v_sim,dfBoxPlot,v_resamp,var,longBusqueda):
    box_plot_data = [dfBoxPlot.loc[dfBoxPlot[v_resamp] == mes_i,var].dropna() for mes_i in np.sort(dfBoxPlot[v_resamp].unique())]
    box_plot_labels = [ 'Enero','Febrero','Marzo','Abril','Mayo','Junio',
                        'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    # Arma curvas de Max, Med y Min
    # df_est_mensual = df.groupby([v_resamp]).agg({ var: ["max","mean","min"]}).reset_index()
    #df_est_mensual.set_index(df_est_mensual[v_resamp], inplace=True)
    #del df_est_mensual[v_resamp]
    #df_est_mensual.columns = ['_'.join(col) for col in df_est_mensual.columns.values]

    if var == 'Caudal':
        label_text = 'Caudal [m'+r'$^3$'+'/s]'
    if var == 'Nivel':
        label_text = 'Nivel [m]'
    
    # Grafico
    fig = plt.figure(figsize=(15, 8))
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(df_obs[v_resamp], df_obs[v_obs],s=50,c='blue',label='Ultimos '+str(longBusqueda)+' Obs.')
    ax.scatter(df_sim[v_resamp], df_sim[v_sim],s=50,c='red',label='Caudal Pronosticado')
    
    #sns.boxplot(data=df_mensual, x="month", y="Caudal",color="skyblue")
    ax.boxplot(box_plot_data,patch_artist=True,labels=box_plot_labels,boxprops={'fill': None})
    plt.title(nomEst)    
    plt.grid(True,axis='y', which='both', color='0.75', linestyle='-.',linewidth=0.3)
    plt.tick_params(axis='y', labelsize=14)
    plt.tick_params(axis='x', labelsize=14,rotation=20)
    plt.xlabel('Mes', size=18)
    plt.ylabel(label_text, size=18)
    plt.legend(prop={'size':16},loc=0,ncol=1)
    plt.show()
    plt.close()

def ErrorXPersistencia(nomEst : str,
                       df : DataFrame,
                       var : str,
                       l_obs : int,
                       l_prono : int,
                       vent_resamp : str="month",
                       plot : bool = True,
                       connBBDD=None,
                       skip_first_years : int = 2) -> DataFrame:
    """
    Calcula error de pronóstico de método persistencia (hindcast)

    Parameters:
    -----------
        nomEst:      Nombre Estacion

        df:          Df con columna de fecha-variable

        var:         Nombre de la variable

        l_obs:       long serie hacia atrás

        l_prono:     longitud del prono

        vent_resamp: Ventana temporal del resampleo

        Plot=True

        connBBDD=None

        skip_first_years : int = 2
    
    Returns
    -------
    df_errorXMes : DataFrame
    """
    logging.debug('Calcula Error x Mes: %s' % str(nomEst))
    df_errorXMes = DataFrame(columns=['mes_%i' % i for i in range(1,l_prono+1,1)])

    # Corta el df. Saca los primeros años y los ultimos l_prono meses
    df_clip = df[skip_first_years * 12:-l_prono].dropna() #l_obs

    if connBBDD != None:
        NombreTabla = 'Salidas_Persist'
        cur = connBBDD.cursor()
        cur.execute('DROP TABLE IF EXISTS '+NombreTabla+';')
    
    def calcError(mes,yr):
        mes_select = int(mes)
        yr_select = int(yr)
        df_prono, percentil = MetodoPersistencia(df,var,mes_select,yr_select,l_obs,l_prono,vent_resamp,Prono=False)
        
        if df_prono["%s_Obs" % var].isna().sum() == 0:
            if len(df_prono) < l_prono:
                raise Exception("Hindcast length at month %i, year %i is too short (%i < %i)" % (mes,yr, len(df_prono), l_prono))
            df_prono['Dif_Prono'] = df_prono["%s_Prono" % var] - df_prono["%s_Obs" % var]
            df_errorXMes.loc[len(df_errorXMes)] = df_prono["Dif_Prono"].values[:l_prono] # [df_prono.loc[0,'Dif_Prono'],df_prono.loc[1,'Dif_Prono'],df_prono.loc[2,'Dif_Prono']]

            if connBBDD != None:
                df_prono['nombre'] = nomEst
                df_prono['year'] = yr_select
                df_prono['mes_ant'] = df_prono.index + 1
                df_prono = df_prono[['nombre','year','month','mes_ant',var+'_Obs',var+'_Prono','Dif_Prono']]
                df_prono.to_sql(NombreTabla, con = connBBDD, if_exists='append',index=False)    # Guarda en BBDD
        
    df_clip.apply(
            lambda  row: calcError(row['month'],row['year']),
            axis=1)
    
    if connBBDD != None: connBBDD.commit()

    if plot:
        box_plot_data = [df_errorXMes[MesAnt] for MesAnt in df_errorXMes.columns]
        box_plot_labels = [MesAnt for MesAnt in df_errorXMes.columns]

        if var == 'Caudal':
            label_text = 'Caudal [m'+r'$^3$'+'/s]'
        if var == 'Nivel':
            label_text = 'Nivel [m]'
        else:
            label_text = 'variable [-]'

        fig = plt.figure(figsize=(15, 8))
        ax = fig.add_subplot(1, 1, 1)

        ax.boxplot(box_plot_data,patch_artist=True,labels=box_plot_labels,boxprops={'fill': 'skyblue'})

        plt.grid(True,axis='y', which='both', color='0.75', linestyle='-.',linewidth=0.3)
        plt.tick_params(axis='y', labelsize=14)
        plt.tick_params(axis='x', labelsize=14,rotation=0)
        plt.xlabel('Mes', size=18)
        plt.ylabel(label_text, size=18)
        #plt.legend(prop={'size':16},loc=0,ncol=1)
        plt.show()
        plt.close()

    return df_errorXMes

def getValueOfQuantile(
        data : DataFrame, 
        month : int, 
        quantile : float,
        month_column : str="month", 
        value_column : str = "valor"):
    return data.loc[data[month_column] == month,value_column].dropna().quantile(quantile)

def getQuantile(
        data : DataFrame, 
        month : int, 
        value : float,
        month_column : str="month",
        value_column : str="valor" ):
    if np.isnan(value):
        raise ValueError("Invalid value: nan not allowed")
    quantile = (data.loc[data[month_column] == month,value_column].dropna() < value).mean()
    if np.isnan(quantile):
        raise Exception("Quantile for value %s not found in data" % str(value))
    return quantile