import os
import jsonschema
from pathlib import Path
import yaml

def getSchema(
        name : str,
        rel_base_path : str = "data/schemas/json"
    ) -> tuple[dict,jsonschema.validators.RefResolver]:
    """
    Reads schema from json or yaml, returns dict of schemas and jsonschema resolver

    Parameters:
    -----------
    name : str
        Schema name
    
    rel_base_path : str = "data/schemas/json"
        Relative base path of the schemas files

    Returns:
    --------
    (dict of parsed schemas, resolver) : tuple[dict,jsonschema.validators.RefResolver]
    """
    schemas = {}
    plan_schema = open("%s/%s/%s.json" % (os.environ["PYDRODELTA_DIR"], rel_base_path, name.lower()))
    schemas[name] = yaml.load(plan_schema,yaml.CLoader)
    base_path = Path("%s/%s" % (os.environ["PYDRODELTA_DIR"], rel_base_path))
    resolver = jsonschema.validators.RefResolver(
        base_uri=f"{base_path.as_uri()}/",
        referrer=True,
    )
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
        instance=instancedict,
        schema=schema,
        resolver=resolver)

def getSchemaAndValidate(
        params : dict,
        name : str,
        rel_base_path : str = "data/schemas/json"
    ):
    """
    Validate dict against json schema
    
    Parameters:
    -----------
    params : dict

        Dict to validate

    name : str

        Name of the schema. Used to find the jsonschema file in rel_base_path
    
    rel_base_path : str = "data/schemas/json"
    
        Path where to find jsonschema files
    
    Raises:
    -------
    jsonschema.exceptions.ValidationError:

        if the instance is invalid

    jsonschema.exceptions.SchemaError:

        if the schema itself is invalid
    """
    schemas, resolver = getSchema(name, rel_base_path)
    return validate(params, schemas[name], resolver)