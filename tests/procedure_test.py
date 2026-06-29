from pydrodelta.procedure import Procedure
from pydrodelta.procedures import UHLinearChannelProcedure
from unittest import TestCase
from pandas import DataFrame, read_csv, to_datetime, DatetimeIndex, Series
from pydrodelta.create_procedure import createProcedure, loadProcedure
from numpy.typing import NDArray
from numpy import array

class Test_Procedure(TestCase):
    
    def test_create(self):
        procedure = Procedure(
            1
        )
        self.assertIsInstance(procedure, Procedure)
    
    def test_loaded_boundaries(self):
        p = UHLinearChannelProcedure.load("tests/data/procedures/loaded_proc_test.yml")
        assert isinstance(p, Procedure)
        assert len(p.boundaries) == 1
        assert len(p.outputs) == 1
        assert isinstance(p.boundaries[0].data, DataFrame)
        assert isinstance(p.outputs[0].data, DataFrame)
        assert len(p.boundaries[0].data) == 8
        assert len(p.outputs[0].data) == 8

        p.loadInput()

        assert p.input is not None
        assert len(p.input) == 1
        assert isinstance(p.input[0], DataFrame)
        assert len(p.input[0]) == 8

        pivot_input = p.loadInput(inplace=False,pivot=True)
        assert isinstance(pivot_input, DataFrame)
        assert len(pivot_input) == 8
        assert len(pivot_input.columns) == 2
        assert "input" in pivot_input.columns
        assert "tag_input" in pivot_input.columns
        assert all(pivot_input["tag_input"] == "inline")


    def test_loaded_boundaries_run(self):

        p = UHLinearChannelProcedure.load("tests/data/procedures/loaded_proc_test.yml")

        p.run(load_output_obs=True)

        assert p.output_obs is not None
        assert len(p.output_obs) == 1
        assert isinstance(p.output_obs[0], DataFrame)
        assert len(p.output_obs[0]) == 8
        assert "valor" in p.output_obs[0].columns

        assert p.output is not None
        assert len(p.output) == 1
        assert isinstance(p.output[0], DataFrame)
        assert len(p.output[0]) == 8
        assert "valor" in p.output[0].columns

        inout = p.pivotInOut()
        assert isinstance(inout, DataFrame)
        assert "input" in inout.columns
        assert "output" in inout.columns
        assert "output_obs" in inout.columns

        # p.data alias for p.pivotInOut()
        assert isinstance(p.data, DataFrame)
        assert len(p.data) == 8
        assert "input" in p.data.columns
        assert "output" in p.data.columns
        assert "output_obs" in p.data.columns

    def test_loadProcedure_run(self):

        p = loadProcedure("tests/data/procedures/loaded_proc_test.yml")

        p.run(load_output_obs=True)

        assert p.output_obs is not None
        assert len(p.output_obs) == 1
        assert isinstance(p.output_obs[0], DataFrame)
        assert len(p.output_obs[0]) == 8
        assert "valor" in p.output_obs[0].columns

        assert p.output is not None
        assert len(p.output) == 1
        assert isinstance(p.output[0], DataFrame)
        assert len(p.output[0]) == 8
        assert "valor" in p.output[0].columns

        inout = p.pivotInOut()
        assert isinstance(inout, DataFrame)
        assert "input" in inout.columns
        assert "output" in inout.columns
        assert "output_obs" in inout.columns

        # p.data alias for p.pivotInOut()
        assert isinstance(p.data, DataFrame)
        assert len(p.data) == 8
        assert "input" in p.data.columns
        assert "output" in p.data.columns
        assert "output_obs" in p.data.columns

    def test_direct_tvp_list(self):
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= [
                    [
                        ("2020-01-01T03:00:00.000Z",1.1),
                        ("2020-01-02T03:00:00.000Z",1.2),
                        ("2020-01-03T03:00:00.000Z",1.3),
                        ("2020-01-04T03:00:00.000Z",1.4),
                        ("2020-01-05T03:00:00.000Z",1.5),
                        ("2020-01-06T03:00:00.000Z",1.6),
                        ("2020-01-07T03:00:00.000Z",1.7),
                        ("2020-01-08T03:00:00.000Z",1.8)
                    ]
                ],
            outputs=[
                    [
                        ("2020-01-01T03:00:00.000Z",0.9),
                        ("2020-01-02T03:00:00.000Z",1.0),
                        ("2020-01-03T03:00:00.000Z",1.1),
                        ("2020-01-04T03:00:00.000Z",1.2),
                        ("2020-01-05T03:00:00.000Z",1.3),
                        ("2020-01-06T03:00:00.000Z",1.4),
                        ("2020-01-07T03:00:00.000Z",1.5),
                        ("2020-01-08T03:00:00.000Z",1.6)
                    ]
            ]            
        )

        p.run(load_output_obs=True)

        run_assertions(p)

    def test_direct_df_list(self):
        input = DataFrame([
                    ["2020-01-01T03:00:00.000Z",1.1],
                    ["2020-01-02T03:00:00.000Z",1.2],
                    ["2020-01-03T03:00:00.000Z",1.3],
                    ["2020-01-04T03:00:00.000Z",1.4],
                    ["2020-01-05T03:00:00.000Z",1.5],
                    ["2020-01-06T03:00:00.000Z",1.6],
                    ["2020-01-07T03:00:00.000Z",1.7],
                    ["2020-01-08T03:00:00.000Z",1.8]
                ],columns=["timestart","valor"])
        input["timestart"] = to_datetime(input["timestart"])
        input = input.set_index("timestart")
        output = DataFrame([
                    ["2020-01-01T03:00:00.000Z",0.9],
                    ["2020-01-02T03:00:00.000Z",1.0],
                    ["2020-01-03T03:00:00.000Z",1.1],
                    ["2020-01-04T03:00:00.000Z",1.2],
                    ["2020-01-05T03:00:00.000Z",1.3],
                    ["2020-01-06T03:00:00.000Z",1.4],
                    ["2020-01-07T03:00:00.000Z",1.5],
                    ["2020-01-08T03:00:00.000Z",1.6]
                ],columns=["timestart","valor"])
        output["timestart"] = to_datetime(output["timestart"])
        output = output.set_index("timestart")
        p = createProcedure(
            "UHLinearChannel",
            id="uh_test",
            parameters={
                "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries=[
                input
            ],
            outputs=[
                output
            ]
        )

        p.run(load_output_obs=True)

        run_assertions(p)

    def test_raise_bad_procedure_type(self):
        self.assertRaises(
            ValueError, 
            createProcedure,
            "BadProcedureType",
            id="uh_test",
            parameters={
                "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries=[
                DataFrame([
                    ["2020-01-01T03:00:00.000Z",1.1],
                    ["2020-01-02T03:00:00.000Z",1.2],
                    ["2020-01-03T03:00:00.000Z",1.3],
                    ["2020-01-04T03:00:00.000Z",1.4],
                    ["2020-01-05T03:00:00.000Z",1.5],
                    ["2020-01-06T03:00:00.000Z",1.6],
                    ["2020-01-07T03:00:00.000Z",1.7],
                    ["2020-01-08T03:00:00.000Z",1.8]
                ],columns=["timestart","valor"])
            ],
            outputs=[
                DataFrame([
                    ["2020-01-01T03:00:00.000Z",0.9],
                    ["2020-01-02T03:00:00.000Z",1.0],
                    ["2020-01-03T03:00:00.000Z",1.1],
                    ["2020-01-04T03:00:00.000Z",1.2],
                    ["2020-01-05T03:00:00.000Z",1.3],
                    ["2020-01-06T03:00:00.000Z",1.4],
                    ["2020-01-07T03:00:00.000Z",1.5],
                    ["2020-01-08T03:00:00.000Z",1.6]
                ],columns=["timestart","valor"])
            ]
        )

    def test_from_csv(self):
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= "tests/data/csv/inputoutput.csv",
            outputs="tests/data/csv/inputoutput.csv"     
        )

        p.run(load_output_obs=True)

        run_assertions(p)

    def test_from_df(self):

        data = read_csv("tests/data/csv/inputoutput.csv", index_col=0, parse_dates=True)
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= data,
            outputs= data
        )

        p.run(load_output_obs=True)

        run_assertions(p)

    def test_from_series(self):

        data = read_csv("tests/data/csv/inputoutput.csv", index_col=0, parse_dates=True)
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= [data.input],
            outputs= [data.output]
        )

        p.run(load_output_obs=True)

        run_assertions(p)

    def test_from_df_no_datetimeindex(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= data,
            outputs= data
        )

        p.run(load_output_obs=True)

        run_assertions(p)
        assert p.data is not None
        assert isinstance(p.data.index, DatetimeIndex)
        assert min(p.data.index).isoformat()[0:10] == '2000-01-01'

    def test_from_dflist_no_datetimeindex(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= [ data[["input"]].rename(columns={"input":"valor"}) ],
            outputs= [ data[["output"]].rename(columns={"output":"valor"}) ]
        )

        p.run(load_output_obs=True)

        run_assertions(p)
        assert p.data is not None
        assert isinstance(p.data.index, DatetimeIndex)
        assert min(p.data.index).isoformat()[0:10] == '2000-01-01'

    def test_from_series_no_datetimeindex(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= [data.input],
            outputs= [data.output]
        )

        p.run(load_output_obs=True)

        run_assertions(p)
        assert p.data is not None
        assert isinstance(p.data.index, DatetimeIndex)
        assert min(p.data.index).isoformat()[0:10] == '2000-01-01'

    def test_from_series_timestart_time_interval(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= [data.input],
            outputs= [data.output],
            timestart="2026-05-01",
            time_interval="1h"
        )

        p.run(load_output_obs=True)

        run_assertions(p)
        assert p.data is not None
        assert isinstance(p.data.index, DatetimeIndex)
        assert min(p.data.index).isoformat()[0:19] == '2026-05-01T00:00:00'
        assert max(p.data.index).isoformat()[0:19] == '2026-05-01T07:00:00'


    def test_from_list_of_float_timestart_time_interval(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= [data.input.tolist()],
            outputs= [data.output.tolist()],
            timestart="2026-05-01",
            time_interval="1h"
        )

        p.run(load_output_obs=True)

        run_assertions(p)
        assert p.data is not None
        assert isinstance(p.data.index, DatetimeIndex)
        assert min(p.data.index).isoformat()[0:19] == '2026-05-01T00:00:00'
        assert max(p.data.index).isoformat()[0:19] == '2026-05-01T07:00:00'

    def test_from_array(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= array([data.input.tolist()]),
            outputs= array([data.output.tolist()]),
            timestart="2026-05-01",
            time_interval="1h"
        )

        p.run(load_output_obs=True)

        run_assertions(p)
        assert p.data is not None
        assert isinstance(p.data.index, DatetimeIndex)
        assert min(p.data.index).isoformat()[0:19] == '2026-05-01T00:00:00'
        assert max(p.data.index).isoformat()[0:19] == '2026-05-01T07:00:00'

    def test_bias_correction(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= array([data.input.tolist()]),
            outputs= array([data.output.tolist()]),
            timestart="2026-05-01",
            time_interval="1h",
            bias_correction=True
        )
        assert p.bias_correction is True
        p.run(load_output_obs=True)

    def test_bias_correction_(self):

        data = read_csv("tests/data/csv/inputoutput.csv")
        p = UHLinearChannelProcedure(
            id="uh_test",
            parameters={
                    "u": [0.13,0.28,0.18,0.16,0.12,0.07,0.05,0.01]
            },
            boundaries= array([data.input.tolist()]),
            outputs= array([data.output.tolist()]),
            timestart="2026-05-01",
            time_interval="1h",
            bias_correction=False
        )
        assert p.bias_correction is False
        p.run(load_output_obs=True)
        assert p.output_obs is not None
        obs = p.output_obs[0]["valor"]
        assert isinstance(obs, Series)
        assert p.output is not None
        sim = p.output[0]["valor"]
        assert isinstance(sim, Series)
        meandif_before = obs.mean() - sim.mean()
        p.run_bias_correction()
        sim_after = p.output[0]["valor"]
        assert isinstance(sim_after, Series)
        meandif_after = obs.mean() - sim_after.mean()
        assert meandif_after < meandif_before
        self.assertAlmostEqual(meandif_after, 0, 4)


def run_assertions(p):
    assert p.output_obs is not None
    assert len(p.output_obs) == 1
    assert isinstance(p.output_obs[0], DataFrame)
    assert len(p.output_obs[0]) == 8
    assert "valor" in p.output_obs[0].columns

    assert p.output is not None
    assert len(p.output) == 1
    assert isinstance(p.output[0], DataFrame)
    assert len(p.output[0]) == 8
    assert "valor" in p.output[0].columns

    assert isinstance(p.data, DataFrame)
    assert len(p.data) == 8
    assert "input" in p.data.columns
    assert "output" in p.data.columns
    assert "output_obs" in p.data.columns

