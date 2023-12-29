from pydrodelta.procedure_function import ProcedureFunction, ProcedureBoundary
import logging
import json
import pydrodelta.util as util
from pydrodelta.a5 import createEmptyObsDataFrame


class Procedure():
    """
    A Procedure defines an hydrological, hydrodinamic or static procedure which takes one or more NodeVariables from the Plan as boundary condition, one or more NodeVariables from the Plan as outputs and a ProcedureFunction. The input is read from the selected boundary NodeVariables and fed into the ProcedureFunction which produces an output, which is written into the output NodeVariables
    """
    def __init__(self,params,plan):
        self.id = params["id"]
        self._plan = plan
        self.initial_states = params["initial_states"] if "initial_states" in params else []
        if params["function"]["type"] in procedureFunctionDict:
            self.function_type = procedureFunctionDict[params["function"]["type"]]
        else:
            logging.warn("Procedure init: class %s not found. Instantiating abstract class ProcedureFunction" % params["function"]["type"])
            self.function_type = ProcedureFunction
        # self.function = self.function_type(params["function"])
        if isinstance(params["function"],dict): # read params from dict
            self.function = self.function_type(params["function"],self)
        else: # if not, read from file
            f = open(params["function"])
            self.function = self.function_type(json.load(f),self)
            f.close()
        # self.procedure_type = params["procedure_type"]
        self.parameters = params["parameters"] if "parameters" in params else []
        self.time_interval = util.interval2timedelta(params["time_interval"]) if "time_interval" in params else None
        self.time_offset = util.interval2timedelta(params["time_offset"]) if "time_offset" in params else None
        self.input = None # <- boundary conditions
        self.output = None
        self.states = None
        self.procedure_function_results = None
        self.save_raw = params["save_raw"] if "save_raw" in params else None
    def loadInput(self,inline=True,pivot=False):
        """
        Carga las variables de borde definidas en self.boundaries. De cada elemento de self.boundaries toma .data y lo concatena en una lista. Si pivot=True, devuelve un DataFrame con 
        """
        if pivot:
            data = createEmptyObsDataFrame(extra_columns={"tag":str})
            columns = ["valor","tag"]
            for boundary in self.function.boundaries:
                if boundary._variable.data is not None and len(boundary._variable.data):
                    rsuffix = "_%s_%i" % (str(boundary.node_id), boundary.var_id) 
                    data = data.join(boundary._variable.data[columns][boundary._variable.data.valor.notnull()],how='outer',rsuffix=rsuffix,sort=True)
            for column in columns:
                del data[column]
            # data = data.replace({np.NaN:None})
        else:
            data = []
            for boundary in self.function.boundaries:
                if not boundary.optional:
                    try:
                        boundary.assertNoNaN()
                    except AssertionError as e:
                        raise Exception("load input error at node %i, variable, %i: %s" % (boundary.node_id, boundary.var_id, str(e)))
                data.append(boundary._variable.data.copy())
        if inline:
            self.input = data
        else:
            return data
    def run(self,inline=True,save_raw=None):
        """
        Run self.function.run()

        :param inline: if True, writes output to self.output, else returns output (array of seriesData)
        """
        save_raw = save_raw if save_raw is not None else self.save_raw
        output, procedure_function_results, raw_results = self.function.run(input=None)
        self.procedure_function_results = procedure_function_results
        if self.procedure_function_results.states is not None:
            self.states = self.procedure_function_results.states
        if inline:
            self.output = output
        else:
            return output
        if save_raw is not None:
            if raw_results is not None:
                try:
                    with open(save_raw, 'w') as f:
                        raw_results.to_csv(f)
                except IOError as e:
                    print(f"Couldn't write to file ({e})")
            else:
                logging.warn("Procedure function produced no raw_results. Skipping save_raw")
    def getOutputNodeData(self,node_id,var_id,tag=None):
        """
        Extracts single series from output using node id and variable id

        :param node_id: node id
        :param var_id: variable id
        :returns: timeseries dataframe
        """
        index = 0
        for o in self.outputs:
            if o.var_id == var_id and o.node_id == node_id:
                if self.output is not None and len(self.output) <= index + 1:
                    return self.output[index]
            index = index + 1
        raise("Procedure.getOutputNodeData error: node with id: %s , var %i not found in output" % (str(node_id), var_id))
        # col_rename = {}
        # col_rename[node_id] = "valor"
        # data = self.output[[node_id]].rename(columns = col_rename)
        # if tag is not None:
        #     data["tag"] = tag
        # return data
    def outputToNodes(self):
        if self.output is None:
            logging.error("Procedure output is None, which means the procedure wasn't run yet. Can't perform outputToNodes.")
            return
        # output_columns = self.output.columns
        index = 0
        for o in self.function.outputs:
            if o._variable.series_sim is None:
                logging.warn("series_sim not defined for output %s" % o.name)
                continue
            if index + 1 > len(self.output):
                logging.error("Procedure output for node %s variable %i not found in self.output. Skipping" % (str(o.node_id),o.var_id))
                continue
            o._variable.concatenate(self.output[index])
            for serie in o._variable.series_sim:
                # logging.debug("output serie %i, data: %s" % (index, str(self.output[index])))
                serie.setData(data=self.output[index]) # self.getOutputNodeData(o.node_id,o.var_id))
                serie.applyOffset()
            index = index + 1
    
from pydrodelta.hecras import HecRasProcedureFunction
from pydrodelta.polynomial import PolynomialTransformationProcedureFunction
from pydrodelta.muskingumchannel import MuskingumChannelProcedureFunction
from pydrodelta.grp import GRPProcedureFunction
from pydrodelta.linear_combination import LinearCombinationProcedureFunction
from pydrodelta.expression import ExpressionProcedureFunction
from pydrodelta.sacramento_simplified import SacramentoSimplifiedProcedureFunction
from pydrodelta.sac_enkf import SacEnkfProcedureFunction

procedureFunctionDict = {
    "ProcedureFunction": ProcedureFunction,
    "HecRas": HecRasProcedureFunction,
    "HecRasProcedureFunction": HecRasProcedureFunction,
    "PolynomialTransformationProcedureFunction": PolynomialTransformationProcedureFunction,
    "Polynomial": PolynomialTransformationProcedureFunction,
    "MuskingumChannel": MuskingumChannelProcedureFunction,
    "MuskingumChannelProcedureFunction": MuskingumChannelProcedureFunction,
    "GRP": GRPProcedureFunction,
    "GRPProcedureFunction": GRPProcedureFunction,
    "LinearCombination": LinearCombinationProcedureFunction,
    "Expression": ExpressionProcedureFunction,
    "SacramentoSimplified": SacramentoSimplifiedProcedureFunction,
    "SacEnKF": SacEnkfProcedureFunction
}
