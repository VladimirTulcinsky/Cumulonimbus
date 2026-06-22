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

    @abstractmethod
    def pretty_print_tf_output(self, **kwargs):
        """
        For each application, output information that is required for the user to run the application.
        """
        raise NotImplementedError()

    def get_flag(self):
        """
        Return the flag for this application. Override in each app configuration.
        Returns None if no flag is configured.
        """
        return None
    def get_hints(self):
        """
        Return a dict mapping hint level (int) to hint text.
        Level 1 is the most gentle nudge; higher levels are more explicit.
        """
        return {}

    mitre_ttps = []

    def print_mitre_ttps(self):
        if not self.mitre_ttps:
            return
        print("\n###############################################")
        print("#         MITRE ATT&CK Techniques            #")
        print("###############################################")
        for ttp in self.mitre_ttps:
            print(f"[{ttp['id']}] {ttp['name']}: {ttp['url']}")


class ConfigurationException(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
