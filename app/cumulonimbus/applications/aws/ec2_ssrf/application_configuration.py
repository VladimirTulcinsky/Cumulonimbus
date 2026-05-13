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

    def get_difficulty(self):
        return "Beginner"

    def get_hints(self):
        return {
            1: "The web app fetches any URL you pass to ?url=. Think about what internal endpoints are reachable from inside the EC2 instance.",
            2: "The EC2 Instance Metadata Service (IMDS) is reachable at http://169.254.169.254/. Try fetching /latest/meta-data/iam/security-credentials/",
            3: "Fetch http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name> via the SSRF endpoint to get temporary AWS credentials, then use them with the AWS CLI to access S3.",
        }

    def get_flag(self):
        return "Cumulonimbus{Th4tW4sCh33sy}"

    def pretty_print_tf_output(self, app_id, output):
        """
        Get the value of a Terraform output.

        :param app_id:                      The application ID
        :param output:                      The output name
        :return:                            The output value
        """
        if not output:
            return
        print("###############################################")
        print("#             Attacker Credentials            #")
        print("###############################################")
        print("[1] aws_access_key_id:" +
              output["attacker_aws_access_key_id"]["value"])
        print("[2] aws_secret_access_key:" +
              output["attacker_aws_secret_access_key"]["value"])
        print("These credentials are valid for the application: {}".format(app_id))
