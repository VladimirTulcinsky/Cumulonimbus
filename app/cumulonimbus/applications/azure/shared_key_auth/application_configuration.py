from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        """
        Given parameters, this runs code that is required for each vulnerable application to run correctly.
        """
        pass

    def get_difficulty(self):
        return "Advanced"

    def get_hints(self):
        return {
            1: "The user has Storage Account Contributor. This role exposes the account's shared key via az storage account keys list — use it to browse the storage containers.",
            2: "One container holds the function app's JavaScript source. Download it, modify it to output the managed identity token (curl IMDS), then re-upload and trigger the function via HTTP.",
            3: "Call http://169.254.169.254/msi/token?resource=https://vault.azure.net from inside the function. Use the returned token with az keyvault secret show to read the 'flag' secret.",
        }

    def get_flag(self):
        return "Cumulonimbus{SharedKeyAuthorizationShouldBeDisabled}"

    def pretty_print_tf_output(self, app_id, output):
        """
        Get the value of a Terraform output.

        :param app_id:                      The application ID
        :param output:                      The output name
        :return:                            The output value
        """
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] This is your primary domain: " +
              output["domain_name"]["value"])
        print("[2] Log in with this user: " +
              output["user_name"]["value"])
        print("[3] The password is: " +
              output["user_password"]["value"])
