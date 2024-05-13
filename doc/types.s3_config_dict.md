# Table of Contents

* [pydrodelta.types.s3\_config\_dict](#pydrodelta.types.s3_config_dict)
  * [s3ConfigDict](#pydrodelta.types.s3_config_dict.s3ConfigDict)

<a id="pydrodelta.types.s3_config_dict"></a>

# pydrodelta.types.s3\_config\_dict

<a id="pydrodelta.types.s3_config_dict.s3ConfigDict"></a>

## s3ConfigDict Objects

```python
class s3ConfigDict(TypedDict)
```

url : str
    s3 api base url
access_key : str    
    access key
secret_key : str
    secret key
secure : bool
    If true, use https else, use http
bucket_name : str
    s3 bucket name

