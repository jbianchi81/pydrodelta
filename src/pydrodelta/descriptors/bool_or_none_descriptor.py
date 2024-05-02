class BoolOrNoneDescriptor:
    """Boolean or None attribute default None"""
    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        if value is None:
            instance.__dict__[self._name] = None
        else:
            try:
                instance.__dict__[self._name] = bool(value)
            except ValueError:
                raise ValueError(f'"{self._name}" must be a boolean or None') from None
