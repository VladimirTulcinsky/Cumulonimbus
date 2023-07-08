from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
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
        key_pair_path = utils.get_key_pair_path('ec2_ssrf')
        os.system("ssh-keygen -t rsa -b 4096 -f {} -N ''".format(key_pair_path))
        print("Key pair for ec2_ssrf located at {}. The keys should only be used for debugging purposes.".format(
            key_pair_path))
        return key_pair_path

    def pretty_print_tf_output(self, app_id, output):
        """
        Get the value of a Terraform output.

        :param app_id:                      The application ID
        :param output:                      The output name
        :return:                            The output value
        """
        print("###############################################")
        print("#             Attacker Credentials            #")
        print("###############################################")
        print("[1] aws_access_key_id:" +
              output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key:" +
              output["attacker_aws_secret_access_key"]["value"])
        print("These credentials are valid for the application: {}".format(app_id))
