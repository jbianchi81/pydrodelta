import pandas
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

def adjustSeriesArima(
    data : pandas.DataFrame,
    k = 1.68):
    """Adjust Arima model to residues

    Args:
        data (pandas.DataFrame): column "valor" contains "truth" values, column "valor_sim" contains "simulated" values
        k (float, optional): confidence level multiplier. Defaults to 1.68.

    Returns:
        Tuple[ARIMA, pandas.DataFrame]]: fitted ARIMA model, dataframe with predictions
    """
    
    # Ajustar modelo de regresión lineal
    model = np.polyfit(data['valor_sim'], data['valor'], 1)
    
    # Modelo ARIMA sobre los residuos
    residuals = data['valor'] - data['valor_sim']
    arima_model = ARIMA(residuals, order=(1, 0, 1)).fit()
    model_error = arima_model.get_forecast(steps=len(data))
    
    # Predicciones futuras
    last_obs_date = data[data["valor"].notna()].index[-1]
    v0 = data.loc[last_obs_date, 'valor']
    data_future = data[data.index > last_obs_date]
    
    lo = model_error.conf_int()["lower y"]
    up = model_error.conf_int()["upper y"]
    mean_err = model_error.predicted_mean
    
    error_modeled_serie = pandas.DataFrame({
        'valor_sim_mean': data_future['valor_sim'],
        'valor_sim_up': data_future['valor_sim'] + arima_model.scale * k,
        'valor_sim_do': data_future['valor_sim'] - arima_model.scale * k,
        'valor_sim_err_do': data_future['valor_sim'] + lo,
        'valor_sim_err_mean': data_future['valor_sim'] + mean_err,
        'valor_sim_err_up': data_future['valor_sim'] + up
    }, index=data_future.index)
    
    # Agregar la primera fila con v0 repetido
    first_row = pandas.DataFrame([[v0] * error_modeled_serie.shape[1]], index=[last_obs_date], columns=error_modeled_serie.columns)
    error_modeled_serie = pandas.concat([first_row, error_modeled_serie])
    
    return arima_model, pandas.concat([data,error_modeled_serie], axis=1)

