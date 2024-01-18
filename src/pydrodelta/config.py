import yaml
import os

def loadConfig():
    config_file = open("%s/config/config.yml" % os.environ["PYDRODELTA_DIR"]) # "src/pydrodelta/config/config.json")
    config = yaml.load(config_file,yaml.CLoader)
    config_file.close()

    defaults_file = open("%s/config/defaults.yml" % os.environ["PYDRODELTA_DIR"]) # "src/pydrodelta/config/config.json")
    defaults = yaml.load(defaults_file,yaml.CLoader)
    defaults_file.close()

    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    return config

config = loadConfig()
