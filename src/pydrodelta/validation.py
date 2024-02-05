import os
import jsonschema
from pathlib import Path
import yaml

def getSchema(name:str,rel_base_path:str="data/schemas/json"):
    """
    Reads schema from json or yaml, returns dict of schemas and jsonschema resolver
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

def validate(params:dict,schema:dict,resolver:jsonschema.validators.RefResolver):
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
    schemas, resolver = getSchema(name, rel_base_path)
    return validate(params, schemas[name], resolver)