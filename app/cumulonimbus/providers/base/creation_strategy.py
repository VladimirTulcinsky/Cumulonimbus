from abc import ABCMeta, abstractmethod


class CreationStrategy(metaclass=ABCMeta):
    """
    This class represents a Creation strategy.
    """

    @abstractmethod
    def create(self, **kwargs):
        """
        TODO:
        """
        raise NotImplementedError()


class CreationException(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
