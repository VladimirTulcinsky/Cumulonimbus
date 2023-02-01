from abc import ABCMeta, abstractmethod


class ApplicationConfigurationAbstract(metaclass=ABCMeta):
    """
    Each vulnerable application could need specific logic.
    e.g. creation of ssh keys
    """

    @abstractmethod
    def configure_application(self, **kwargs):
        """
        Given parameters, this runs code that is required for each vulnerable application to run correctly.
        """
        raise NotImplementedError()


class ConfigurationException(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
