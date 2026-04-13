import yaml
from pathlib import Path
import click
from dataclasses import dataclass
from typing import TypedDict, cast, Any

@dataclass
class AppState:
    run_create: bool = False

class ApiConfig(TypedDict):
    url : str
    token : str

class LogConfig(TypedDict):
    filename : str

class ConfigDict(TypedDict):
    input_api : ApiConfig
    output_api: ApiConfig
    log : LogConfig

state = AppState()

CONFIG_PATH = Path.home() / ".pydrodelta.yml"

DEFAULT_CONFIG : ConfigDict = {
    "input_api": {
        "url": "https://alerta.ina.gob.ar/a5",
        "token": "my_token",
    },
    "output_api": {
        "url": "http://localhost:3005",
        "token": "my_token",
    },
    "log": {
        "filename": str(Path.home() / "pydrodelta.log")
    }
}

def deep_fill(data: dict, defaults: dict) -> dict:
    for k, v in defaults.items():
        if k not in data or data[k] is None:
            data[k] = v
        elif isinstance(v, dict) and isinstance(data[k], dict):
            deep_fill(data[k], v)
    return data

def prompt(field, default):
    value = input(f"{field} [{default}]: ").strip()
    return value if value else default


def create_config(defaults = DEFAULT_CONFIG) -> ConfigDict:
    print("Please enter configuration values.\n")

    defaults = deep_fill(cast(dict[str, Any], defaults), cast(dict[str, Any], DEFAULT_CONFIG))

    cfg : ConfigDict = {
        "input_api": {
            "url": prompt("Input API URL", defaults["input_api"]["url"]),
            "token": prompt("Input API token", defaults["input_api"]["token"]),
        },
        "output_api": {
            "url": prompt("Output API URL", defaults["output_api"]["url"]),
            "token": prompt("Output API token", defaults["output_api"]["token"]),
        },
        "log": {
            "filename": prompt("Log file path", defaults["log"]["filename"])
        }
    }

    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(f"\nConfig saved to {CONFIG_PATH}")
    return cfg

def loadConfig() -> ConfigDict:
    if not CONFIG_PATH.exists():
        print("Config file not found.")
        state.run_create = True
        return create_config()

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def editConfig():
    cfg = loadConfig()
    return create_config(cfg)

config = loadConfig()

@click.command()
@click.pass_context
def edit_config(self):
    if not state.run_create:
        editConfig()
