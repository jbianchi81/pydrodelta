import yaml
from .config import config
from .util import coalesce
from .a5 import Crud
from .descriptors.dict_descriptor import DictDescriptor
from .persistence import S3Client
from .types.api_config_dict import ApiConfigDict
from .types.s3_config_dict import s3ConfigDict

class Base():
    """An abstract class"""

    input_api_config = DictDescriptor()

    output_api_config = DictDescriptor()
    
    a5_config = DictDescriptor()

    input_crud : Crud

    output_crud : Crud
        
    s3_client : S3Client

    def __init__(self,
        input_api_config : ApiConfigDict = None, 
        output_api_config : ApiConfigDict = None, 
        s3_config : s3ConfigDict = None
        ):
        self.input_api_config = coalesce(input_api_config,config["input_api"] if "input_api" in config else None)
        self.output_api_config = coalesce(output_api_config,config["output_api"] if "output_api" in config else None)
        self.s3_config = coalesce(s3_config,config["s3"] if "s3" in config else None)
        self.input_crud = Crud(**self.input_api_config) if self.input_api_config is not None else None
        self.output_crud = Crud(**self.output_api_config) if self.output_api_config is not None else None
        self.s3_client = S3Client(self.s3_config)

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