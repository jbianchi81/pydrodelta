from abc import ABC, abstractmethod
from .base import Base
from pathlib import Path
from typing import Any, TypedDict, Literal, Union, Optional, Dict, List
from .analysis import run_analysis_from_file
from .simulation import run_plan_from_file
import click
import logging

class Task(Base):
    def __init__(
            self, 
            config_file: Union[str, Path],
            options: Optional[Dict[str, Any]] = None,
            base_path: Optional[Union[str, Path]] = None
        ):
        super().__init__(base_path=base_path)
        self.config_file = self.resolve_path(config_file)
        self.options = options or {}

    @abstractmethod
    def run(self):
        """Execute the task."""
        pass


class SimulationTask(Task):
    def run(self):
        print(f"Running simulation with {self.config_file}")
        run_plan_from_file(
            self.config_file,
            self.options.get("csv"),
            self.options.get("json"),
            self.options.get("graph_file"),
            self.options.get("export_corrida_json"),
            self.options.get("export_corrida_csv"),
            self.options.get("pivot") or False,
            self.options.get("upload") or False,
            self.options.get("include_prono") or None,
            self.options.get("verbose") or False,
            self.options.get("output_stats"),
            self.options.get("output_results"),
            self.options.get("plot_var"),
            self.options.get("pretty") or False,
            self.options.get("output_analysis"),
            self.options.get("quiet") or False,
            self.options.get("upload_prono") or False,
            self.options.get("save_upload_response"),
            self.options.get("input_api"),
            self.options.get("output_api"),
            self.options.get("save_calibration_result")
        )

class AnalysisTask(Task):
    def run(self):
        logging.info(f"Running analysis with {self.config_file}")
        run_analysis_from_file(
            self.config_file,
            self.options.get("csv"),
            self.options.get("json"),
            self.options.get("graph_file"),
            self.options.get("pivot") or False,
            self.options.get("upload") or False,
            self.options.get("include_prono") or False,
            self.options.get("verbose") or False,
            self.options.get("upload_series_prono") or False,
            self.options.get("upload_series_output_as_prono") or False,
            self.options.get("plot_var"),
            self.options.get("pretty") or False,
            self.options.get("input_api"),
            self.options.get("output_api")
        )

class BaseTaskDict(TypedDict):
    type : Literal["simulation","analysis"]
    config_file : str
    options : dict

def parse_task(cfg : BaseTaskDict, base_path : Optional[Union[Path, str]]=None) -> Union[SimulationTask,AnalysisTask]:
    task_type = cfg.get("type")
    if task_type is None:
        raise ValueError("Missing task.type")
    if task_type == "simulation":
        return SimulationTask(cfg["config_file"], cfg["options"], base_path=base_path)
    elif task_type == "analysis":
        return AnalysisTask(cfg["config_file"], cfg["options"], base_path=base_path)
    else:
        raise ValueError("Bad task.type. Must be one of 'simulation', 'analysis'")

class Workflow(Base):
    def __init__(
            self, 
            tasks: Union[Task, List[Task], BaseTaskDict, List[BaseTaskDict]], 
            name: Optional[str]="Workflow", 
            base_path: Optional[Union[str,Path]]=None,
            on_exception_continue: Optional[bool]=None
            ):
        super().__init__(base_path=base_path)
        if isinstance(tasks, Task):
            tasks = [tasks]
        elif isinstance(tasks, dict):
            tasks = [parse_task(tasks, self.base_path)]

        self.tasks = [task if isinstance(task, Task) else parse_task(task, self.base_path) for task in tasks]
        self.name = name
        self.on_exception_continue = on_exception_continue if on_exception_continue is not None else False

    def run(self):
        for task in self.tasks:
            try:
                task.run()
            except Exception as e:
                if self.on_exception_continue:
                    logging.warning("Catched exception at task %s. Message: %s" % (task.config_file, str(e)))
                else:
                    raise e


@click.command()
@click.pass_context
@click.argument('config_file', type=str)
def run_workflow(self, config_file):
    """Run workflow. A workflow is a sequence of simulation and analysis tasks

    Args:
        config_file (str): Workflow description
    """
    run_workflow_from_file(config_file)

def run_workflow_from_file(config_file : str):
    """Run workflow. A workflow is a sequence of simulation and analysis tasks
    
    Args:
        config_file (str): Workflow description
    """
    workflow = Workflow.load(config_file)
    workflow.run()