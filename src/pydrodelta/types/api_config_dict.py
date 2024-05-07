from typing import TypedDict

class ApiConfigDict(TypedDict):
    """
        url : str
            api base url
        token : str    
            api authorization token
    """
    url : str
    token : str