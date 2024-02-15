from pydrodelta.util import tryParseAndLocalizeDate

class DatetimeDescriptor:
    """Datetime descriptor
    
    Reads: for absolute date: ISO-8601 datetime string or datetime.datetime. For relative date: dict (duration key-values) or float (decimal number of days)
    
    Returns: datetime.datetime"""
    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        try:
            instance.__dict__[self._name] = tryParseAndLocalizeDate(value) if value is not None else None
        except ValueError:
            raise ValueError(f'"{self._name}" must be a date or a duration') from None
