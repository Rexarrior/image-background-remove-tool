class Singleton(type):
    """
    Metaclass to create a Singleton class.

    It is used as a decorator @singleton above the definition
    of a class.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Returns an instance of the decorated class, creating it if necessary.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
