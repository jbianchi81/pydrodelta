from ..procedure_function import ProcedureFunction, ProcedureFunctionResults
from ..validation import getSchemaAndValidate
from ..function_boundary import FunctionBoundary
from a5client import createEmptyObsDataFrame
from typing import Union, List, Tuple
from pandas import DataFrame, concat
from matplotlib import pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from pytz import timezone
from pydrodelta.descriptors.dataframe_descriptor import DataFrameDescriptor
import numpy as np
import logging

class AnalogyProcedureFunction(ProcedureFunction):
    """Analogy forecast procedure"""

    _boundaries = [
        FunctionBoundary({"name": "input", "optional": True})
    ]

    _outputs = [
        FunctionBoundary({"name": "output"})
    ]
    
    @property
    def search_length(self) -> int:
        """search_length : longitud de la serie para buscar Analogas"""
        return int(self.parameters["search_length"])
    
    @property
    def forecast_length(self) -> int:
        """forecast_length : longitud del pronostico"""
        return int(self.parameters["forecast_length"])
    
    @property
    def order_by(self) -> str:
        """Ordena por"""
        return self.parameters["order_by"] if "order_by" in self.parameters else "RMSE"

    @property
    def ascending(self) -> str:
        """Ordena ascendente"""
        return bool(self.parameters["ascending"]) if "ascending" in self.parameters else True

    @property
    def number_of_analogs(self) -> int:
        """Cantidad de series que toma"""
        return int(self.parameters["number_of_analogs"]) if "number_of_analogs" in self.parameters else 5

    @property
    def time_window(self) -> int:
        """Ventana temporal"""
        return self.parameters["time_window"] if "time_window" in self.parameters else "month"

    errores = DataFrameDescriptor()

    df_prono_analog = DataFrameDescriptor()

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
                - search_length : int
                    longitud de la serie para buscar Analogas
                - forecast_length : int
                    longitud del pronostico
                - order_by : "Nash" | "CoefC" |"RMSE" | "SPEDS" | "ErrVol" = "RMSE"
                    Ordena Por
                - ascending : bool = True
                    Sort ascending
                - number_of_analogs : int = 5
                    Cantidad de series que toma
                - time_window : "year" | "month" | "day" | "yrDay" | "wkDay" = "month"
                    Ventana temporal
        
        **kwargs : see ..procedure_function.ProcedureFunction
        """
        super().__init__(parameters = parameters, **kwargs)
        getSchemaAndValidate(dict(kwargs, parameters = parameters),"AnalogyProcedureFunction")
        self.errores = None
        self.df_prono_analog = None

    
    def run(
        self,
        input : List[DataFrame] = None
        ) -> Tuple[List[DataFrame],ProcedureFunctionResults]:
        """Run the function procedure
        
        Parameters:
        -----------
        input : list of DataFrames
            Boundary conditions. If None, runs .loadInput

        Returns:
        Tuple[List[DataFrame],ProcedureFunctionResults] : first element is the procedure function output (list of DataFrames), while second is a ProcedureFunctionResults object"""
        if input is None:
            input = self._procedure.loadInput(inplace=False,pivot=False)

        inici_0 = time.time()

        if self._procedure._plan.forecast_date.day > 27:
            mes_select = self._procedure._plan.forecast_date.month
            yr_select = self._procedure._plan.forecast_date.year
        else:
            if self._procedure._plan.forecast_date.month == 1:
                mes_select = 12
                yr_select = self._procedure._plan.forecast_date.year-1
            else:
                mes_select = self._procedure._plan.forecast_date.month-1
                yr_select = self._procedure._plan.forecast_date.year

        data = input[0].copy()
        CreaVariablesTemporales(data)

        ### Metodo Analogias.

        ## 1 - 1MesPart x Analogia
        # Transfroma los datos
        TransfDatos(data,"valor",self.time_window,PlotTransf=False)
        self.df_prono_analog = MetodoAnalogia(data,"valor",mes_select,yr_select,self.time_window,self.search_length, self.forecast_length, self.order_by, self.ascending, self.number_of_analogs)
        
        # Mes a formato fecha
        self.df_prono_analog['month'] = self.df_prono_analog.apply(lambda x: month2Date(x.year, x.month), axis=1)

        output = self.df_prono_analog[['month','Prono']].rename(columns={"month":"timestart", "Prono":"valor"}).set_index("timestart")
              
        
        ## 2 - Calcula errores X serie
        self.errores = MetodoAnalogia_errores_v2(self.boundaries[0].node_id,data,"valor",self.time_window,self.parameters,outputfile=self._procedure.save_results) # connBBDD=conn
        
        return (
            [output], 
            ProcedureFunctionResults(
                data = self.df_prono_analog,
                parameters = self.parameters
            )
        )
    
def TransfDatos(df : DataFrame, column : str = "valor", time_window : str = "month",PlotTransf=False):
    #### 1 - Transfroma los datos
    # create log-transformed data
    df['LogVar'] = np.log(df[column])  # Con var < 0 tira warning
    # Normaliza los datos transformados
    df['LogVar_Est'] = np.nan
    for w in df[time_window].unique():
        w_mean = df.loc[df[time_window] == w,'LogVar'].dropna().mean()
        w_std = df.loc[df[time_window] == w,'LogVar'].dropna().std()
        # Normaliza los datos
        df.loc[df[time_window]==w,'LogVar_Est'] = (df.loc[df[time_window]==w,'LogVar'] - w_mean)/w_std
    if PlotTransf:   # plots datos transformados
        fig, axs = plt.subplots(nrows=1, ncols=3)
        #create histograms
        axs[0].hist(df[column], edgecolor='black')
        axs[1].hist(df['LogVar'], edgecolor='black')
        axs[2].hist(df['LogVar_Est'], edgecolor='black')
        #add title to each histogram
        axs[0].set_title('Original Data')
        axs[1].set_title('Log-Transformed Data')
        axs[2].set_title('Log-Transformed-Norm Data')
        plt.show()
        plt.close()

def CreaVariablesTemporales(df : DataFrame):   # Variables Temporales
    df.insert(0, 'year', df.index.year)
    df.insert(1, 'month', df.index.month)
    df.insert(2, 'day', df.index.day)
    df.insert(3, 'yrDay', df.index.dayofyear)
    df.insert(4, 'wkDay', df.index.isocalendar().week)

def MetodoAnalogia(df,var,mes_obj,yr_obj,vent_resamp,search_length,forecast_length,order_by,ascending,number_of_analogs):

    # Compara un año con sus parecidos
    Result_Indic = CalcIndicXFecha(df,yr_obj,mes_obj,search_length)
    
    if False:   # Compara Indicadores
        x = 'ErrVol_norm'
        y = 'CoefC_norm'
        fig = plt.figure(figsize=(15, 8))
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(Result_Indic[x], Result_Indic[y],2,label=x+' - '+y)
        # ax.plot(Result_Indic.index, Result_Indic['nivel'],'-',label=yr_sim,linewidth=2)
        plt.grid(True, which='both', color='0.75', linestyle='-.',linewidth=0.5)
        plt.tick_params(axis='both', labelsize=16)
        plt.xlabel('Fecha', size=18)
        plt.legend(prop={'size':16},loc=2,ncol=2 )
        plt.show()
        plt.close()
    
    # Busca los indicadores para el año seleccionado
    R_Indic_i = Result_Indic[(Result_Indic['YrObs'] == yr_obj) & (Result_Indic['MesObs'] == mes_obj)] 

    # Ordena y filtra los primeros n
    R_Indic_i =R_Indic_i.sort_values(by=order_by,ascending=ascending).reset_index()

    # Arma el Df de datos Obs para la fecha seleccionada
    fecha_Obj = df.query("year=="+str(yr_obj)+" and month=="+str(mes_obj)) # Busca la fecha seleccionada
    idx_select = fecha_Obj.index[0].to_pydatetime() # + 1                                          # Toma el id de la fecha seleccionada
    idx_fecha_f = idx_select + relativedelta(months=forecast_length)

    index_i = []
    while idx_select < idx_fecha_f:
        index_i.append(idx_select)
        idx_select = idx_select + relativedelta(months=1)
    dfObj = DataFrame(index = index_i,columns=['year','month',var])
    dfObj[vent_resamp] = range(mes_obj+1, mes_obj+1+forecast_length, 1)
    ### Solo para vent_resamp='month' ####
    dfObj['year'] = yr_obj
    dfObj.loc[dfObj[vent_resamp]  > 12, 'year'] = dfObj.loc[dfObj[vent_resamp]  > 12, 'year'] + 1
    dfObj.loc[dfObj[vent_resamp]  > 12, 'month'] = dfObj.loc[dfObj[vent_resamp]  > 12, vent_resamp] - 12

    df_union = dfObj.copy()
    cols_var = [var,'LogVar_Est']

    n_sim_sin_nan = 0
    par_comp = DataFrame(index=range(0,number_of_analogs,1),columns=R_Indic_i.columns)

    for index, row in R_Indic_i.iterrows():
        yr_sim = row['YrSim']
        # Arma el Df para comparar con el seleccionado.
        fecha_sim = df.query("year=="+str(yr_sim)+" and month=="+str(mes_obj))
        idx_sim = fecha_sim.index[0].to_pydatetime() # + 1
        idx_sim_f = idx_sim + relativedelta(months=forecast_length)
        dfSim = df[idx_sim:idx_sim_f].copy().dropna()

        if len(dfSim) < 3:
            print(yr_sim,' Con Faltantes.')
            continue
        else:
            par_comp.iloc[n_sim_sin_nan] = R_Indic_i.iloc[index]
            dfSim = dfSim[['month',]+ cols_var]
            dfSim = dfSim.rename(columns={cols_var[0]:int(yr_sim),cols_var[1]:str(int(yr_sim))+'_Transf'})
            df_union = df_union.merge(dfSim, on='month')
            n_sim_sin_nan += 1
            if n_sim_sin_nan == 5: break

    # Calculo de los pesos
    par_comp['wi'] = 1/par_comp['RMSE']
    par_comp['wi'] = par_comp['wi']/par_comp['wi'].sum()
    
    # Multiplica por los pesos
    for index, row in par_comp.iterrows():
        yrstr = str(row['YrSim'])+'_Transf'
        df_union[yrstr] = df_union[yrstr] * row['wi']


    # Lista de pronos transformados a sumar
    list_years_analog = [str(yr)+'_Transf' for yr in par_comp['YrSim'].to_list()]
    df_union['Prono'] = df_union[list_years_analog].sum(axis=1)

    # Invierte transformacion
    df_union['mes_mean'] = [df.loc[df['month'] == mes,'LogVar'].dropna().mean() for mes in df_union['month']]
    df_union['mes_std'] =  [df.loc[df['month'] == mes,'LogVar'].dropna().std() for mes in df_union['month']]

    df_union['Prono'] = df_union['Prono']*df_union['mes_std'] + df_union['mes_mean']
    df_union['Prono'] = np.exp(df_union['Prono'])
    
    # dfObj_0 = dfObj_0[['year','month',var]].copy()
    # df_Obs_previo = df_union[['year','month',var]].copy()
    # frames = [dfObj_0, df_Obs_previo]	
    # df_Obs_previo = concat(frames).reset_index(drop=True)
    
    #df_union["meses_ord"] = df_union["month"] + 6 - mes_selct
    #df_union.loc[df_union["meses_ord"]  > 12, 'meses_ord'] = df_union.loc[df_union["meses_ord"]  > 12, 'meses_ord'] - 12
    #PlotAnalogias(nomEst,df_union,df_Obs_previo,var,par_comp,df,vent_resamp)

    return df_union

# Calcula indicadores para la fecha seleccionada.
def CalcIndicXFecha(df,year_obj,mes_obj,longBusqueda):
    df_indicadores = DataFrame(columns=['YrObs','MesObs','YrSim','nobs', 'Vobs_media', 'Vsim_media', 'Nash', 'CoefC','RMSE', 'SPEDS', 'ErrVol'])
    variable_transf = 'LogVar_Est'
    # Busca la fecha seleccionada
    fecha_Obj = df.query("year=="+str(year_obj)+" and month=="+str(mes_obj))
    # Toma el id de la fecha seleccionada
    idx_select = fecha_Obj.index[0].to_pydatetime()

    # Arma el Df de datos Obs para la fecha seleccionada
    idx_fecha_fin = idx_select # + relativedelta(months=1)
    idx_fecha_inicio = idx_fecha_fin - relativedelta(months=longBusqueda)
    dfObj_0 = df.loc[idx_fecha_inicio:idx_fecha_fin].copy()

    if dfObj_0[variable_transf].isna().sum() > 0:
        raise ValueError("Null values found in time series")
        # return False, dfObj_0, 0

    for yr_sim in df['year'].unique():
        if yr_sim == year_obj:
            continue # <=
        # Arma el Df para comparar con el seleccionado.
        fecha_sim = df.query("year=="+str(yr_sim)+" and month=="+str(mes_obj))
        if len(fecha_sim) == 0:
            continue
        idx_sim = fecha_sim.index[0].to_pydatetime()
        idx_sim_fin = idx_sim # +1
        idx_sim_inicio = idx_sim_fin-relativedelta(months=longBusqueda)

        dfSim = df[idx_sim_inicio:idx_sim_fin].copy()
        dfSim = dfSim[['month',variable_transf]]
        dfSim = dfSim.rename(columns={variable_transf:yr_sim})
        df_union = dfObj_0.merge(dfSim, on='month')

        # Si hay faltantes no calcula los indicadores
        if df_union[yr_sim].isna().sum() > 0: 
            continue
        if len(df_union) == 0: 
            continue

        df_indic_i = IndicadoresDeAjuste(df_union,variable_transf,yr_sim,mes_obj,n_var_obs=year_obj)
        df_indicadores = concat([df_indicadores,df_indic_i])

    # Agrega indicadores
    variables = ['Nash','CoefC','RMSE','SPEDS','ErrVol']
    for var in variables:
        df_indicadores[var+'_norm'] = (df_indicadores[var] - df_indicadores[var].min())/(df_indicadores[var].max()-df_indicadores[var].min())

    df_indicadores['Score'] = df_indicadores['Nash_norm'] + df_indicadores['CoefC_norm'] - df_indicadores['RMSE_norm'] + df_indicadores['SPEDS_norm'] - df_indicadores['ErrVol_norm']
    Result_Indic = df_indicadores.sort_values(by='Score',ascending=False)
    # return dfObj_0, Result_Indic
    return Result_Indic

def IndicadoresDeAjuste(df : DataFrame,VarObs : str,VarSim : str,mes_selct,n_var_obs=None,n_var_sim=None):
    Vobs_media = round(np.mean(df[VarObs]),1)
    Vsim_media = round(np.mean(df[VarSim]),1)

    #Nash y Sutcliffe
    F = (np.square(np.subtract(df[VarSim], df[VarObs]))).sum()
    F0 = (np.square(np.subtract(df[VarObs], np.mean(df[VarObs])))).sum()
    E_var = round(100*(F0-F)/F0,3)

    #Coeficiente de correlación (r)
    x = df[VarObs]
    y = df[VarSim]
    r_var = np.round(np.corrcoef(x, y),4)[0, 1]

    #Error cuadratico medio
    df1aux = df.dropna()
    rms_var = np.sqrt(((np.square(np.subtract(df1aux[VarSim], df1aux[VarObs]))).sum())/len(df1aux))
    rms_var = round(rms_var,3)

    #SPEDS
    b = list()
    Qobs_ant = 0
    Qsim_ant = 0
    for index, row in df.iterrows():
        if (row[VarObs] - Qobs_ant)*(row[VarSim] - Qsim_ant) >= 0:
            bi = 1
        else:
            bi = 0
        Qobs_ant = row[VarObs]
        Qsim_ant = row[VarSim]
        b.append(bi)
    SPEDS_var = round(float(100*sum(b)/len(b)),2)

    #Error Volumetrico OJO! esta pasado a volumen diario y no a mensual
    volSim = (df[VarSim].multiply(86400)).sum()
    volObs = (df[VarObs].multiply(86400)).sum()
    ErrorVolumetrico = round(100 * (volSim - volObs) / volObs,1)

    #volSim = round(volSim,1)
    #volObs = round(volObs,1)
    if n_var_obs==None:
        n_var_obs = VarObs
    if n_var_sim==None:
        n_var_sim =VarSim

    df_i = DataFrame({
        'YrObs':[n_var_obs,],
        'MesObs':[mes_selct,],
        'YrSim':[n_var_sim,], 
        'nobs':[len(df)],
        'Vobs_media':[Vobs_media,], 
        'Vsim_media':[Vsim_media,], 
        'Nash':[E_var,], 
        'CoefC':[r_var,],
        'RMSE':[rms_var,], 
        'SPEDS':[SPEDS_var,], 
        'ErrVol':[ErrorVolumetrico,]
        })
    return  df_i

def month2Date(y,x):
        return datetime(y, x, 1,0,0,0,0, tzinfo=timezone("America/Argentina/Buenos_Aires"))

def MetodoAnalogia_errores_v2(name_Est,df,var,vent_resamp,ParamMetodo,outputfile : str=None,connBBDD=None) -> DataFrame:
    longBusqueda = ParamMetodo['search_length']
    longProno = ParamMetodo['forecast_length']
    orden = ParamMetodo['order_by']
    orde_ascending = ParamMetodo['ascending']
    cantidad = ParamMetodo['number_of_analogs']
    
    if connBBDD != None:
        NombreTabla = 'Salidas_Analog'
        cur = connBBDD.cursor()
        cur.execute('DROP TABLE IF EXISTS '+NombreTabla+';')
    
    # Calcula error
    columnas = ['nombre','year','month','mes_ant','Caudal','Prono','Dif_Prono','E1','E2','E3','E4','E5']
    df_errorXMes = DataFrame(columns=columnas)
    
    # Quita los ultimos 10 años y los primeros "longProno" registros. Porque no van a tener la serie completa.
    df_clip = df[10*12:-longProno].copy()

    # Loop sobre todos los meses desde el inicio de la serie. Saca los primeros 10 años para que los primeros años tengan datos para buscar analogia
    for index, row in df_clip.iterrows():
        # Si hay valores negativos en la serie se le suma el valor minimo.
        # Luego se le vuelve a sumar el valor. Se hace para que el log no tiere error
        min_val = df[var].min()
        if min_val<=0:
            df[var]=df[var]-(min_val-0.01)

        mes_select = int(row['month'])
        yr_select = int(row['year'])
        # if yr_select<1944: continue
        # if mes_selct<9: continue
        # print(mes_selct)
        if mes_select==1: print(yr_select)


        fecha_a_prono = df.query("year=="+str(yr_select)+" and month=="+str(mes_select))     # Busca la fecha seleccionada
        idx_select = fecha_a_prono.index[0].to_pydatetime()                                          # Toma el id de la fecha seleccionada

        # Filtra datos Futuros
        df_pasado = df[:idx_select].copy()

        # Transfroma los datos
        # create log-transformed data
        df_pasado['LogVar'] = np.log(df_pasado[var])

        # Normaliza los datos transformados
        df_pasado['LogVar_Est'] = np.nan

        for mes in df_pasado['month'].unique():
            mes_mean = df_pasado.loc[df_pasado[vent_resamp] == mes,'LogVar'].dropna().mean()
            mes_std = df_pasado.loc[df_pasado[vent_resamp] == mes,'LogVar'].dropna().std()

            # Normaliza los datos
            df_pasado.loc[df_pasado['month']==mes,'LogVar_Est'] = (df_pasado.loc[df_pasado['month']==mes,'LogVar'] - mes_mean)/mes_std
        
        # Calclula Indicadores
        conNAN, df_indicadores, dfObj_0 = CalcIndic_Analog_error(df_pasado,yr_select,mes_select,longBusqueda,longProno)
        if conNAN: 
            print('Datos Faltantes: ',mes_select,yr_select)
            continue
        
        # Ordena y filtra los primeros n
        df_indicadores =df_indicadores.sort_values(by=orden,ascending=orde_ascending).reset_index()
        df_indicadores['YrObs'] = df_indicadores['YrObs'].astype('int')
        df_indicadores['YrSim'] = df_indicadores['YrSim'].astype('int')

        # Arma el Df de datos Obs para la fecha seleccionada
        fecha_Obj = df.query("year=="+str(yr_select)+" and month=="+str(mes_select))     # Busca la fecha seleccionada
        idx_select = fecha_Obj.index[0].to_pydatetime() # + 1                                      # Toma el id de la fecha seleccionada
        idx_fecha_f = idx_select + relativedelta(months=longProno)
        dfObj = df[idx_select:idx_fecha_f].copy()
        # del dfObj['Count']

        #print(dfObj_0)
        #print(dfObj)

        df_union = dfObj.copy()
        cols_var = [var,'LogVar_Est']
        n_sim_sin_nan = 0
        par_comp = DataFrame(index=range(0,cantidad,1),columns=df_indicadores.columns)
        for index, row in df_indicadores.iterrows():
            yr_sim = int(row['YrSim'])
            # Arma el Df para comparar con el seleccionado.
            fecha_sim = df_pasado.query("year=="+str(yr_sim)+" and month=="+str(mes_select))
            idx_sim = fecha_sim.index[0].to_pydatetime() # + 1
            idx_sim_f = idx_sim + relativedelta(months=longProno)
            dfSim = df_pasado[idx_sim:idx_sim_f].copy().dropna()
            if len(dfSim) < 3:
                print('\t',yr_sim,' con Faltantes.')
                continue
            else:
                par_comp.iloc[n_sim_sin_nan] = df_indicadores.iloc[index]
                dfSim = dfSim[['month',]+ cols_var]
                dfSim = dfSim.rename(columns={cols_var[0]:int(yr_sim),cols_var[1]:str(int(yr_sim))+'_Transf'})
                df_union = df_union.merge(dfSim, on='month')
                n_sim_sin_nan += 1
                if n_sim_sin_nan == 5: break
        
        # Calculo de los pesos
        par_comp['wi'] = 1/par_comp['RMSE']
        par_comp['wi'] = par_comp['wi']/par_comp['wi'].sum()

        par_comp['YrObs'] = par_comp['YrObs'].astype('int')
        par_comp['YrSim'] = par_comp['YrSim'].astype('int')
        
        # Multiplica por los pesos
        for index, row in par_comp.iterrows():
            yrstr = str(row['YrSim'])+'_Transf'
            df_union[yrstr] = df_union[yrstr] * row['wi']
        
        list_years_analog = [str(yr)+'_Transf' for yr in par_comp['YrSim'].to_list()]
        df_union['Prono'] = df_union[list_years_analog].sum(axis=1)

        df_union['mes_mean'] = [df_pasado.loc[df_pasado['month'] == mes,'LogVar'].dropna().mean() for mes in df_union['month']]
        df_union['mes_std'] =  [df_pasado.loc[df_pasado['month'] == mes,'LogVar'].dropna().std() for mes in df_union['month']]

        df_union['Prono'] = df_union['Prono']*df_union['mes_std'] + df_union['mes_mean']
        df_union['Prono'] = np.exp(df_union['Prono'])

        df_union['Dif_Prono'] = df_union['Prono'] - df_union[cols_var[0]]

        df_union['nombre'] = name_Est
        df_union['mes_ant'] = df_union.index + 1

        # Agrega los ensambles para guardarlos
        lst_ensam = par_comp['YrSim'].to_list()
        i = 0
        Ensam_columns = []
        for ensam_i  in lst_ensam:
            i +=1
            df_union = df_union.rename(columns={ensam_i: 'E'+str(i)})
            Ensam_columns += ['E'+str(i),]

        columns_save = ['nombre','year','month','mes_ant',cols_var[0],'Prono','Dif_Prono']+ Ensam_columns
        df_union = df_union[columns_save]

        if min_val<0:
            df_union[var]=df[var]+min_val
            for Ei in Ensam_columns:
                df_union[Ei]  = df_union[Ei]+(min_val-0.01)
        if connBBDD != None:
                df_union.to_sql(NombreTabla, con = connBBDD, if_exists='append',index=False)    # Guarda en BBDD
                connBBDD.commit()
        
        df_errorXMes = concat([df_errorXMes,df_union]) if len(df_errorXMes) else df_union
    if outputfile is not None:
        df_errorXMes.to_csv(outputfile,index=False) # ruta_salidas+'/Errores/'+name_Est+'_Error_X_anticipo.csv'
    return df_errorXMes

def CalcIndic_Analog_error(df,year_obj,mes_obj,longBusqueda,longProno):
    # True or False. False: si la serie objetivo tiene faltatnes  
    # df_indicadores: Df con los indicadores
    # dfObj_0: Df con La serie objetivo, serie a comprar con resto
    columnas = ['YrObs','MesObs','YrSim','nobs', 'Vobs_media', 'Vsim_media', 'Nash', 'CoefC','RMSE', 'SPEDS', 'ErrVol']
    df_indicadores = DataFrame(columns=columnas)

    variable_transf = 'LogVar_Est'
    # Busca la fecha seleccionada
    fecha_Obj = df.query("year=="+str(year_obj)+" and month=="+str(mes_obj))
    # Toma el id de la fecha seleccionada
    idx_select = fecha_Obj.index[0].to_pydatetime()

    # Arma el Df de datos Obs para la fecha seleccionada
    idx_fecha_fin = idx_select # +1
    idx_fecha_inicio = idx_fecha_fin - relativedelta(months=longBusqueda)
    dfObj_0 = df[idx_fecha_inicio:idx_fecha_fin].copy()

    if dfObj_0[variable_transf].isna().sum() > 0:
        return True, 0, dfObj_0
    
    # Compara un año con sus parecidos
    for yr_compara in df['year'].unique():   # Loop sobre todos los meses desde el inicio de la serie
        yr_compara = int(yr_compara)

        if yr_compara == year_obj: continue

        # Arma el Df para comparar con el seleccionado.
        fecha_sim = df.query("year=="+str(yr_compara)+" and month=="+str(mes_obj))
        if len(fecha_sim) == 0:continue
        idx_sim = fecha_sim.index[0].to_pydatetime()
        idx_sim_fin = idx_sim # +1
        idx_sim_inicio = idx_sim_fin - relativedelta(months=longBusqueda)

        dfSim = df[idx_sim_inicio:idx_sim_fin].copy()
        dfSim = dfSim[['month',variable_transf]]
        dfSim = dfSim.rename(columns={variable_transf:yr_compara})
        df_union = dfObj_0.merge(dfSim, on='month')

        # Si hay faltantes no calcula los indicadores
        if df_union[yr_compara].isna().sum() > 0: continue
        if len(df_union) == 0: continue

        df_indic_i = IndicadoresDeAjuste(df_union,variable_transf,yr_compara,mes_obj,n_var_obs=year_obj)
        df_indicadores = concat([df_indicadores,df_indic_i]) if len(df_indicadores) else df_indic_i.copy()

    return False, df_indicadores, dfObj_0
