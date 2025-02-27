from unittest import TestCase
from pydrodelta.arima import adjustSeriesArima
from pydrodelta.util import adjustSeries
from pydrodelta.procedure import Procedure
from pandas import DataFrame, date_range
from numpy import nan

class Test_ARIMA(TestCase):

    def test_arima(self):
        data = DataFrame({
            "timestart": date_range(start="2024-01-01", periods=10, freq="D"),
            "valor": [1,2,3,4,5,6,nan,nan,nan,nan],
            "valor_sim": [3,4,5,7,8,9,10,12,13.3,14.5]
        })
        data = data.set_index("timestart")
        arima_model, data_adj = adjustSeriesArima(data)

        self.assertEqual(len(data_adj),len(data))
        self.assertEqual(len(data_adj["adj"].dropna()), 5)
        self.assertEqual(len(data_adj["superior"].dropna()), 5)
        self.assertEqual(len(data_adj["inferior"].dropna()), 5)

    def test_arima_adjust(self):
        data = DataFrame({
            "timestart": date_range(start="2024-01-01", periods=10, freq="D"),
            "valor": [1,2,3,4,5,6,nan,nan,nan,nan],
            "valor_sim": [3,4,5,7,8,9,10,12,13.3,14.5]
        })
        data = data.set_index("timestart")

        adj, tag_adj, fitted_model = adjustSeries(
            sim_df = data[["valor_sim"]],
            truth_df = data[["valor"]],
            method = "arima",
            plot = True,
            return_adjusted_series = True,
            tag_column = None,
            title  = None,
            warmup  = None,
            tail  = None,
            sim_range = None,
            covariables = ["valor_sim"]
        )

        self.assertEqual(len(adj),len(data))
        self.assertEqual(len(adj.dropna()), 5)

    def test_arima_adjust_procedure(self):
        data = DataFrame({
            "timestart": date_range(start="2024-01-01", periods=10, freq="D"),
            "input": [1,2,3,4,5,6,7,8,9,10],
            "output": [3,4,5,7,8,9,nan,nan,nan,nan]
        })
        data = data.set_index("timestart")

        procedure = Procedure(
            id = "test adj arima",
            function = {
                "type": "Expression",
                "expression": "value + 0.5",
                "boundaries": [
                    {
                        "name": "input",
                        "node_variable": [0,0]
                    }
                ],
                "outputs": [
                    {
                        "name": "output",
                        "node_variable": [1,0]
                    }
                ]
            },
            adjust = True,
            adjust_method = "arima",
            warmup_steps = None,
            tail_steps = None,
            error_band = None
        )
        procedure.input = [
            data[["input"]].rename(columns={"input":"valor"})
        ]
        procedure.output_obs = [
            data[["output"]].rename(columns={"output":"valor"})
        ]
        procedure.run(load_input = False, load_output_obs = False)
        
        # print(procedure.output[0])
        self.assertEqual(len(procedure.output),1)
        self.assertEqual(len(procedure.output[0]["valor"]), 10)
        self.assertEqual(len(procedure.output[0]["valor"].dropna()), 10)
        self.assertEqual(len(procedure.output[0]["inferior"].dropna()), 10)
        self.assertEqual(len(procedure.output[0]["superior"].dropna()), 10)
        self.assertEqual(len(procedure.output[0][procedure.output[0].index >= '2024-01-06']["lower"].dropna()), 4)
        self.assertEqual(len(procedure.output[0][procedure.output[0].index >= '2024-01-06']["upper"].dropna()), 4)
