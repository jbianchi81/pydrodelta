from typing import TypedDict

class s3ConfigDict(TypedDict):
    """
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
    """
    url : str
    access_key : str
    secret_key : str
    secure : bool
    bucket_name : str
