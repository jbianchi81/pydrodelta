from pydrodelta.plan import Plan
from pydrodelta.procedures.analogy import AnalogyProcedureFunction, CreaVariablesTemporales, TransfDatos, CalcIndicXFecha
from pydrodelta.util import tryParseAndLocalizeDate
from unittest import TestCase
from pydrodelta.util import createDatetimeSequence
from pandas import DataFrame
import numpy as np

class Test_Analogy(TestCase):

    timestart = (1900,1,1)
    timeend = (2000,1,1)

    index = createDatetimeSequence(
        timeInterval={"months":1},
        timestart = timestart, 
        timeend = timeend
    )
    # genera serie autoregresiva
    phi = 0.8
    sigma = 1
    epsilon = np.random.normal(0, sigma, len(index))
    values = np.zeros(len(index))
    values[0] = epsilon[0]

    for t in range(1, len(index)):
        values[t] = phi * values[t-1] + epsilon[t]

    data = DataFrame({
        "timestart": index,
        "valor": values
    })
    data.set_index("timestart",inplace=True)

    year_obj = 1999
    mes_obj = 12
    longBusqueda = 6

    def test_temp_vars(self):

        data = CreaVariablesTemporales(self.data, inplace=False)
        self.assertTrue("year" in data.columns)
        self.assertTrue("month" in data.columns)
        self.assertTrue("day" in data.columns)
        self.assertTrue("yrDay" in data.columns)
        self.assertTrue("wkDay" in data.columns)

    def test_transf_datos(self):

        data = CreaVariablesTemporales(self.data,inplace=False)
        TransfDatos(data,"valor","month",PlotTransf=False, make_positive=True)
        self.assertTrue("LogVar" in data.columns)
        self.assertTrue("LogVar_Est" in data.columns)
        self.assertEqual(len(data["LogVar"].dropna()),len(data))
        self.assertEqual(len(data["LogVar_Est"].dropna()),len(data))

    def test_calc_indic(self):

        data = CreaVariablesTemporales(self.data,inplace=False)
        TransfDatos(data,"valor","month",PlotTransf=False, make_positive=True)
        df_indicadores = CalcIndicXFecha(data,self.year_obj,self.mes_obj,self.longBusqueda)
        self.assertTrue(df_indicadores["YrSim"].dtype.kind == 'i')

    def test_run(self):
        pf = AnalogyProcedureFunction(
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
