class DictDescriptor:
    """Dict descriptor with default None"""
    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        try:
            instance.__dict__[self._name] = dict(value) if value is not None else None
        except ValueError:
            raise ValueError(f'"{self._name}" must be a dict') from None
