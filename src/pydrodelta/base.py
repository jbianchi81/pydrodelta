import yaml
from .config import config
from .util import coalesce
from .a5 import Crud
from .descriptors.dict_descriptor import DictDescriptor
from .persistence import MinioClient

class Base():
    """An abstract class"""

    config = DictDescriptor()

    input_crud : Crud

    output_crud : Crud

    def __init__(self,config_dict : dict=None):
        self.config = coalesce(config_dict,config)
        self.input_crud = Crud(**self.config["input_api"]) if "input_api" in self.config else None
        self.output_crud = Crud(**self.config["output_api"]) if "output_api" in self.config else None
        self.minio_client = MinioClient(self.config["minio"] if "minio" in self.config else None)

    @classmethod
    def load(cls, file : str, **kwargs):
        """Load configuration from yaml file

        Args:
            file (str): path of yaml configuration file
            **kwargs: additional configuration parameters (dependant on the specific class)

        Returns:
            Plan: an object of this class according to the provided configuration
        """
        t_config = yaml.load(open(file),yaml.CLoader)
        return cls(**t_config,**kwargs)