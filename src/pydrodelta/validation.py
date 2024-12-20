import os
from jsonschema import Draft202012Validator
from pathlib import Path
import yaml
from typing import Tuple
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from referencing.exceptions import Unresolvable
from .config import config
import json
import requests
import re

def getSchema(
        name : str,
        rel_base_path : str = "schemas/json"
    ) -> Tuple[dict,Registry]:
    """
    Reads schema from json or yaml, returns dict of schemas and jsonschema resolver

    Parameters:
    -----------
    name : str
        Schema name
    
    rel_base_path : str = "schemas/json"
        Relative base path of the schemas files

    Returns:
    --------
    (dict of parsed schemas, Registry) : Tuple[dict, referencing.Registry]
    """
    read_stream = open(
        os.path.join(
            config["PYDRODELTA_DIR"],
            rel_base_path,
            "%s.json" % name.lower()
        )
    )
    base_schema = yaml.load(read_stream,yaml.CLoader)
    read_stream.close()
    base_path = Path(
        config["PYDRODELTA_DIR"], 
        rel_base_path
    )
    base_uri = f"{base_path.as_uri()}/${name}"
    return crawl_and_register(base_schema, base_uri, name)
    # registry = Registry()
    # resource = Resource.from_contents(schemas[name])
    # registry = registry.with_resource(base_uri, resource)
    # resolver = jsonschema.validators.RefResolver(
    #     base_uri=f"{base_path.as_uri()}/",
    #     referrer=True,
    # )
    # return schemas, registry # .lookup # resolver

def validate(
    params : dict,
    schema : dict,
    registry : Registry # jsonschema.validators.RefResolver
    ) -> None:
    """
    Validate dict against schema using JSONschema resolver
    
    Parameters:
    ----------
    params : dict
        Dict to validate

    schema : dict
        Schema to validate dict against

    registry : referencing.Registry
        python-jsonschema Registry
    
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
    validator = Draft202012Validator(schema, registry=registry)
    return validator.validate(instancedict)

def getSchemaAndValidate(
        params : dict,
        name : str,
        rel_base_path : str = "schemas/json"
    ):
    """
    Validate dict against json schema
    
    Parameters:
    -----------
    params : dict

        Dict to validate

    name : str

        Name of the schema. Used to find the jsonschema file in rel_base_path
    
    rel_base_path : str = "schemas/json"
    
        Path where to find jsonschema files
    
    Raises:
    -------
    jsonschema.exceptions.ValidationError:

        if the instance is invalid

    jsonschema.exceptions.SchemaError:

        if the schema itself is invalid
    """
    schemas, registry = getSchema(name, rel_base_path)
    return validate(params, schemas[name], registry)

def crawl_and_register(schema : dict, base_uri : str, base_name : str = "base.json", registry : Registry = None) -> Tuple[dict, Registry]:
    """
    Crawls a JSON Schema and registers all referenced schemas into a registry.
    
    Args:
        schema (dict): The root JSON Schema to crawl.
        base_uri (str): The base URI to resolve relative references.
        registry (Registry, optional): The initial registry to update.
        
    Returns:
        dict: dictionary containing the registered schemas
        Registry: The updated registry with all resources registered.
    """
    if registry is None:
        registry = Registry()
    
    # Register the root schema
    resource = Resource.from_contents(schema)
    registry = registry.with_resource(base_uri, resource)

    schemas = {}
    schemas[base_name] = schema
    
    # Crawl schema for $ref fields
    def crawl(schema_part, current_uri):
        if isinstance(schema_part, dict):
            # Handle $defs
            if "$defs" in schema_part:
                for def_name, def_schema in schema_part["$defs"].items():
                    # Register each schema in $defs with a derived URI
                    position = "#/$defs/{def_name}"
                    basename = os.path.basename(current_uri)
                    def_uri = f"{basename}{position}"
                    schemas[def_uri] = def_schema
                    def_resource = Resource.from_contents(def_schema, default_specification=DRAFT202012)
                    registry = registry.with_resource(def_uri, def_resource)
                    # Crawl the $defs schema for nested $refs or $defs
                    crawl(def_schema, def_uri)
            # Check for $ref
            if "$ref" in schema_part:
                ref_uri = schema_part["$ref"]
                ref_uri = re.sub("#.*$","",ref_uri)
                if ref_uri.startswith(("http://", "https://")):
                    abs_uri = ref_uri
                else:
                    # Resolve relative references
                    abs_uri = str(Path(current_uri).parent / ref_uri)
                if ref_uri not in schemas:
                    try:
                        ref_schema = load_schema(abs_uri)
                        schemas[ref_uri] = ref_schema
                        # Load and register the referenced schema
                        ref_resource = Resource.from_contents(ref_schema)
                        registry = registry.with_resource(ref_uri, ref_resource)
                        # Recurse into the referenced schema
                        crawl(ref_schema, abs_uri)
                    except FileNotFoundError:
                        raise FileNotFoundError(f"Referenced schema not found: {abs_uri}")
            else:
                # Crawl nested dictionaries
                for key, value in schema_part.items():
                    crawl(value, current_uri)
        elif isinstance(schema_part, list):
            # Crawl lists
            for item in schema_part:
                crawl(item, current_uri)
    
    crawl(schema, base_uri)
    return schemas, registry

def load_schema(uri):
    """
    Loads a JSON Schema from a URI (file path or URL).
    """
    if uri.startswith(("http://", "https://")):
        response = requests.get(uri)
        response.raise_for_status()
        return response.json()
    else:
        file_path = re.sub("^file:","",uri)
        try:
            with open(Path(file_path), "r") as file:
                schema = json.load(file)
                file.close()
                return schema
        except RecursionError as e:
            raise e
