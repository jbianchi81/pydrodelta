class ListOrDictDescriptor:
    """List or dict descriptor with default None"""
    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        if isinstance(value, (list,tuple)):
            try:
                instance.__dict__[self._name] = value if isinstance(value,list) else list(value)
            except ValueError:
                raise ValueError(f'"{self._name}" must be a list or a dict') from None
        elif value is not None:
            try:
                instance.__dict__[self._name] = dict(value)
            except ValueError:
                raise ValueError(f'"{self._name}" must be a list or a dict') from None
        else:
            instance.__dict__[self._name] = None
