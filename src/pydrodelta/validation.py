import os
import jsonschema
from pathlib import Path
import yaml
from typing import Tuple
from .config import config
import logging
import importlib.resources
from datetime import datetime, date
from collections.abc import Mapping

def to_json_types(obj):
    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, Mapping):
        return {k: to_json_types(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_json_types(v) for v in obj]

    return obj

def getSchema(
        name : str
    ) -> Tuple[dict,jsonschema.validators.RefResolver]:
    """
    Reads schema from json or yaml, returns dict of schemas and jsonschema resolver. Schemas are in pydrodelta.schemas.json

    Parameters:
    -----------
    name : str
        Schema name

    Returns:
    --------
    (dict of parsed schemas, resolver) : Tuple[dict,jsonschema.validators.RefResolver]
    """
    schemas = {}
    with importlib.resources.path("pydrodelta.schemas.json", "") as base_path:
        logging.debug("base path as uri: %s/" % base_path.as_uri())
        resolver = jsonschema.validators.RefResolver(
            base_uri=f"{base_path.as_uri()}/",
            referrer=True,
        )
    with importlib.resources.open_text("pydrodelta.schemas.json", "%s.json" % name.lower()) as f:
        schemas[name] = yaml.safe_load(f)
    return schemas, resolver

def validate(
    params : dict,
    schema : dict,
    resolver : jsonschema.validators.RefResolver
    ) -> None:
    """
    Validate dict against schema using JSONschema resolver
    
    Parameters:
    ----------
    params : dict
        Dict to validate

    schema : dict
        Schema to validate dict against

    resolver : jsonschema.validators.RefResolver
        jsonschema resolver
    
    Raises:
    -------
    jsonschema.exceptions.ValidationError:

        if the instance is invalid

    jsonschema.exceptions.SchemaError:

        if the schema itself is invalid

    """
    instancedict = params.copy()
    if "self" in instancedict:
        del instancedict["self"]
    instancedictkeys = list(instancedict.keys())
    for key in instancedictkeys:
        if instancedict[key] is None:
            del instancedict[key]
    return jsonschema.validate(
        instance=to_json_types(instancedict),
        schema=schema,
        resolver=resolver)

def getSchemaAndValidate(
        params : dict,
        name : str
    ):
    """
    Validate dict against json schema. Schemas are in pydrodelta.schemas.json
    
    Parameters:
    -----------
    params : dict

        Dict to validate

    name : str

        Name of the schema. Used to find the jsonschema file in rel_base_path
        
    Raises:
    -------
    jsonschema.exceptions.ValidationError:

        if the instance is invalid

    jsonschema.exceptions.SchemaError:

        if the schema itself is invalid
    """
    schemas, resolver = getSchema(name)
    # print("Base URI:", resolver.base_uri)
    return validate(params, schemas[name], resolver)