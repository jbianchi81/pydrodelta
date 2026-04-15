import yaml
from .config import config
from .util import coalesce, resolve_path, toMapping
from a5client import Crud
from .descriptors.dict_descriptor import DictDescriptor
from .persistence import S3Client
from .types.api_config_dict import ApiConfigDict
from .types.s3_config_dict import s3ConfigDict
from pathlib import Path
from typing import Optional, Union, overload

class Base():
    """An abstract class"""

    input_api_config = DictDescriptor()

    output_api_config = DictDescriptor()
    
    a5_config = DictDescriptor()

    input_crud : Optional[Crud]

    output_crud : Optional[Crud]
        
    s3_client : Optional[S3Client]

    base_path : Optional[Union[str,Path]]

    def __init__(self,
        input_api_config : Optional[ApiConfigDict] = None, 
        output_api_config : Optional[ApiConfigDict] = None, 
        s3_config : Optional[s3ConfigDict] = None,
        base_path : Optional[Union[str,Path]] = None
        ):
        self.input_api_config = coalesce(input_api_config,config["input_api"] if "input_api" in config else None)
        self.output_api_config = coalesce(output_api_config,config["output_api"] if "output_api" in config else None)
        self.s3_config = coalesce(s3_config,config["s3"] if "s3" in config else None)
        self.input_crud = Crud(**self.input_api_config) if self.input_api_config is not None else None
        self.output_crud = Crud(**self.output_api_config) if self.output_api_config is not None else None
        self.s3_client = S3Client(self.s3_config)
        self.base_path = base_path

    @classmethod
    def load(cls, file : Union[Path,str], **kwargs):
        """Load configuration from yaml file

        Args:
            file (str): path of yaml configuration file
            **kwargs: additional configuration parameters (dependant on the specific class)

        Returns:
            Plan: an object of this class according to the provided configuration
        """
        with open(file) as f:
            t_config = yaml.safe_load(f)
        kwargs["base_path"] = Path(file).resolve().parent
        return cls(**toMapping(t_config),**kwargs)
    
    @overload
    def resolve_path(self, path : Union[str,Path]) -> Path: ...
    @overload
    def resolve_path(self, path : None) -> None: ...
    def resolve_path(self, path : Union[str,Path,None]) -> Union[Path,None]:
        return resolve_path(path, self.base_path) if path is not None else None