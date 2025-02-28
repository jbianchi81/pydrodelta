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
    # lm_coeffs = np.polyfit(data['valor_sim'], data['valor'], 1)
    
    # Predicciones futuras
    last_obs_date = data[data["valor"].notna()].index[-1]
    v0 = data.loc[last_obs_date, 'valor']
    data_future = data[data.index > last_obs_date].copy()
    data_past = data[data.index <= last_obs_date]

    # Modelo ARIMA sobre los residuos
    residuals = data_past['valor'] - data_past['valor_sim']
    arima_model = ARIMA(residuals, order=(1, 0, 1)).fit()
    model_error = arima_model.get_forecast(steps=len(data_future))
    quant_Err = residuals.quantile([.001,.05,.95,.999])
    mean_predicted_mean = sum(model_error.predicted_mean) / len(model_error.predicted_mean)
        
    data_future["lo"] = model_error.conf_int()["lower y"]
    data_future["up"] = model_error.conf_int()["upper y"]
    data_future["mean_err"] = model_error.predicted_mean
    # data_future['superior'] = data_future['valor_sim'] + np.sqrt(np.diag(lm_cov)) * k
    # data_future['inferior'] = data_future['valor_sim'] - np.sqrt(np.diag(lm_cov)) * k
    data_future["lower"] = data_future['valor_sim'] + data_future["lo"]
    data_future["adj"] = data_future['valor_sim'] + data_future["mean_err"]
    data_future["upper"] = data_future['valor_sim'] + data_future["up"]

    # drop columns
    data_future = data_future.drop(columns=["valor","lo","up","mean_err","valor_sim"])
    #set index
    # data_future = data_future.set_index("timestart")
    # Agregar la primera fila con v0 repetido
    # first_row = pandas.DataFrame([[v0] * data_future.shape[1]], index=[last_obs_date], columns=data_future.columns)
    # data_future = pandas.concat([first_row, data_future])
    data_result = pandas.concat([data,data_future], axis=1)
    # adjust past using mean predicted mean 
    data_result["adj"] = data_result["adj"].fillna(data_result["valor_sim"] + mean_predicted_mean)

    return {
        "method": "arima", 
        "quant_Err": quant_Err,
        "mse": arima_model.mse,
        "const": arima_model.params["const"],
        "ar.L1": arima_model.params["ar.L1"],
        "ma.L1": arima_model.params["ma.L1"],
        "sigma2": arima_model.params["sigma2"],
        "order": arima_model.model.order,
        "aic": arima_model.aic,
        "bic": arima_model.bic,
        "hqic": arima_model.hqic,
        "params": arima_model.params.tolist(),  # Convert to list for JSON compatibility
        "pvalues": arima_model.pvalues.tolist(),
        "resid": arima_model.resid.tolist(),
        "fittedvalues": arima_model.fittedvalues.tolist()
        }, data_result