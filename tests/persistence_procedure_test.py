from pydrodelta.plan import Plan
from pydrodelta.procedures.persistence import PersistenceProcedureFunction, getValueOfQuantile, getQuantile
from pydrodelta.util import tryParseAndLocalizeDate
from unittest import TestCase
from pydrodelta.util import createDatetimeSequence
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np

class Test_Persistence(TestCase):

    timestart = (1900,1,1)
    timeend = (2000,1,1)

    index = createDatetimeSequence(
        timeInterval={"months":1},
        timestart = timestart, 
        timeend = timeend
    )
    # genera serie periodica con componente correlacionada
    phi = 0.7
    sigma = 400
    intercept = 1000
    slope = 200
    epsilon = np.random.normal(0, sigma, len(index))

    values = np.zeros(len(index))
    values[0] = intercept + slope * np.sin(np.mod(0,12)*2*np.pi/12) + epsilon[0]

    for t in range(1, len(index)):
        values[t] = (1 - phi) * (intercept + slope * np.sin(np.mod(t,12)*2*np.pi/12) + epsilon[t]) + phi * values[t-1]

    data = DataFrame({
        "timestart": index,
        "valor": values
    })
    data.set_index("timestart",inplace=True)

    year_obj = 1999
    mes_obj = 12
    longBusqueda = 6

    # def test_plot(self):
    #     data_ = self.data.copy()
    #     data_["month"] = data_.index.month
    #     plt.scatter(data_['month'], data_['valor'])
    #     plt.title("Value by Month")
    #     plt.xlabel("Month")
    #     plt.ylabel("Value")
    #     plt.grid(True)
    #     plt.xticks(range(1, 13))
    #     plt.show()        

    def test_get_quantile(self):
        data_ = self.data.copy()
        data_["month"] = data_.index.month
        for i, row in data_.tail(12).iterrows():
            quantile = getQuantile(
                data_, 
                row["month"], 
                row["valor"],
                "month",
                "valor")
            self.assertTrue(quantile > 0)
            self.assertTrue(quantile < 1)


    def test_get_value_of_quantile(self):
        data_ = self.data.copy()
        data_["month"] = data_.index.month
        for month in range(1,13,1):
            quantile = getValueOfQuantile(data_, month, 0.5, "month", "valor")
            self.assertTrue(quantile > data_[data_["month"] == month]["valor"].min())
            self.assertTrue(quantile < data_[data_["month"] == month]["valor"].max())

    def test_run(self):
        pf = PersistenceProcedureFunction(
            parameters={
                "search_length":6,
                "forecast_length": 4
            },
            boundaries = [
                {
                    "name": "input",
                    "node_variable": [1,1]
                }
            ],
            outputs = [
                {
                    "name": "output",
                    "node_variable": [1,1]
                }
            ]
        )

        input = [
            self.data.copy()
        ]

        output, procedure_results = pf.run(input, forecast_date=(2000,1,1))
        self.assertEqual(len(output),1)
        self.assertEqual(len(output[0]),4)
        self.assertTrue("valor" in output[0].columns)
        self.assertIsInstance(output[0]["valor"].sum(),float)
        self.assertNotEqual(output[0]["valor"].sum(),np.nan)
        self.assertEqual(output[0].index[0],tryParseAndLocalizeDate(self.timeend))
        self.assertTrue(pf.percentil > 0)
        self.assertTrue(pf.percentil < 1)

    def test_run_error_band(self):
        pf = PersistenceProcedureFunction(
            parameters={
                "search_length":6,
                "forecast_length": 4
            },
            boundaries = [
                {
                    "name": "input",
                    "node_variable": [1,1]
                }
            ],
            outputs = [
                {
                    "name": "output",
                    "node_variable": [1,1]
                }
            ],
            extra_pars = {
                "add_error_band": True
            }
        )

        input = [
            self.data.copy()
        ]

        output, procedure_results = pf.run(input, forecast_date=(2000,1,1))
        self.assertEqual(len(output),1)
        self.assertEqual(len(output[0]),4)
        self.assertTrue("inferior" in output[0].columns)
        self.assertTrue("superior" in output[0].columns)
        self.assertIsInstance(output[0]["inferior"].sum(),float)
        self.assertNotEqual(output[0]["inferior"].sum(),np.nan)
        self.assertIsInstance(output[0]["superior"].sum(),float)
        self.assertNotEqual(output[0]["superior"].sum(),np.nan)
        self.assertEqual(output[0].index[0],tryParseAndLocalizeDate(self.timeend))
        for i, row in output[0].iterrows():
            self.assertTrue(not np.isnan(row["superior"]))
            self.assertTrue(not np.isnan(row["inferior"]))
            self.assertTrue(row["inferior"] < row["valor"])
            self.assertTrue(row["superior"] > row["valor"])
        for i, row in pf.error_stats.iterrows():
            if i > 0:
                self.assertTrue(row["std"] > pf.error_stats.loc[i-1,"std"])
        # distinct_months = set(pf.errores["month"])
        # for month in distinct_months:
        #     self.assertTrue(month in [12,1,2,3,4,5,6])


    # def test_run_error_band_relative_window(self):
    #     only_last_years = 10
    #     pf = AnalogyProcedureFunction(
    #         parameters={
    #             "search_length":6,
    #             "forecast_length": 4
    #         },
    #         boundaries = [
    #             {
    #                 "name": "input",
    #                 "node_variable": [1,1]
    #             }
    #         ],
    #         outputs = [
    #             {
    #                 "name": "output",
    #                 "node_variable": [1,1]
    #             }
    #         ],
    #         extra_pars = {
    #             "add_error_band": True,
    #             "only_last_years": only_last_years,
    #             "error_forecast_date_window": 1
    #         }
    #     )

    #     input = [
    #         self.data.copy()
    #     ]

    #     output, procedure_results = pf.run(input, forecast_date=(2000,1,1))
    #     self.assertEqual(len(output),1)
    #     self.assertEqual(len(output[0]),4)
    #     self.assertTrue("inferior" in output[0].columns)
    #     self.assertTrue("superior" in output[0].columns)
    #     self.assertIsInstance(output[0]["inferior"].sum(),float)
    #     self.assertNotEqual(output[0]["inferior"].sum(),np.nan)
    #     self.assertIsInstance(output[0]["superior"].sum(),float)
    #     self.assertNotEqual(output[0]["superior"].sum(),np.nan)
    #     self.assertEqual(output[0].index[0],tryParseAndLocalizeDate(self.timeend))
    #     for i, row in output[0].iterrows():
    #         self.assertTrue(row["inferior"] < row["valor"])
    #         self.assertTrue(row["superior"] > row["valor"])
    #     for i, row in pf.error_stats.iterrows():
    #         if i > 0 and i <= 3:
    #             self.assertTrue(row["std"] > pf.error_stats.loc[i-1,"std"])
    #             self.assertTrue(row["count"] >= (only_last_years - 1) * 3 and row["count"] <= only_last_years * 3)
    #     distinct_months = set(pf.errores["month"])
    #     for month in distinct_months:
    #         self.assertTrue(month in [12,1,2,3,4,5,6])
