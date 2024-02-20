# Table of Contents

* [pydrodelta.validation](#pydrodelta.validation)
  * [getSchema](#pydrodelta.validation.getSchema)
  * [validate](#pydrodelta.validation.validate)
  * [getSchemaAndValidate](#pydrodelta.validation.getSchemaAndValidate)

<a id="pydrodelta.validation"></a>

# pydrodelta.validation

<a id="pydrodelta.validation.getSchema"></a>

#### getSchema

```python
def getSchema(
    name: str,
    rel_base_path: str = "data/schemas/json"
) -> tuple[dict, jsonschema.validators.RefResolver]
```

Reads schema from json or yaml, returns dict of schemas and jsonschema resolver

**Arguments**:

  -----------
  name : str
  Schema name
  
  rel_base_path : str = "data/schemas/json"
  Relative base path of the schemas files
  

**Returns**:

  --------
  (dict of parsed schemas, resolver) : tuple[dict,jsonschema.validators.RefResolver]

<a id="pydrodelta.validation.validate"></a>

#### validate

```python
def validate(params: dict, schema: dict,
             resolver: jsonschema.validators.RefResolver) -> None
```

Validate dict against schema using JSONschema resolver

**Arguments**:

  ----------
  params : dict
  Dict to validate
  
  schema : dict
  Schema to validate dict against
  
  resolver : jsonschema.validators.RefResolver
  jsonschema resolver
  

**Raises**:

  -------
  jsonschema.exceptions.ValidationError:
  
  if the instance is invalid
  
  jsonschema.exceptions.SchemaError:
  
  if the schema itself is invalid

<a id="pydrodelta.validation.getSchemaAndValidate"></a>

#### getSchemaAndValidate

```python
def getSchemaAndValidate(params: dict,
                         name: str,
                         rel_base_path: str = "data/schemas/json")
```

Validate dict against json schema

**Arguments**:

  -----------
  params : dict
  
  Dict to validate
  
  name : str
  
  Name of the schema. Used to find the jsonschema file in rel_base_path
  
  rel_base_path : str = "data/schemas/json"
  
  Path where to find jsonschema files
  

**Raises**:

  -------
  jsonschema.exceptions.ValidationError:
  
  if the instance is invalid
  
  jsonschema.exceptions.SchemaError:
  
  if the schema itself is invalid

