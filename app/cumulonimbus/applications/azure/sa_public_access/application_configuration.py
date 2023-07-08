from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        """
        Given parameters, this runs code that is required for each vulnerable application to run correctly.
        """
        pass

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
        print("[1] This is your entrypoint, open your browser and browse to:" +
              output["primary_web_endpoint"]["value"])
        print("As storage accounts must be globally unique, a unique ID will be appended to the storage account name.")
        print("[2] This is your unique application ID: " +
              str(output["cumulonimbus_id"]["value"]) + " ==> cumulonimbus" + str(output["cumulonimbus_id"]["value"]))
