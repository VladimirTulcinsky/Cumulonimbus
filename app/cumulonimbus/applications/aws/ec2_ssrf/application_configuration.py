from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        """
        Given parameters, this runs code that is required for each vulnerable application to run correctly.
        """
        print("Configuring application ec2_ssrf")
        self.__create_key_pair()

    def __create_key_pair(self):
        """
        Create a key pair for the application.

        :param app_id:                      The application ID
        :return:                            The path to the key pair
        """
        key_pair_path = os.path.join(os.path.expanduser("~/.ssh/ec2_ssrf"))
        os.system("ssh-keygen -t rsa -b 4096 -f {} -N ''".format(key_pair_path))
        print("Key pair for ec2_ssrf located at {}. The keys should only be used for debugging purposes.".format(
            key_pair_path))
        return key_pair_path
