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
        return "Beginner"

    def get_hints(self):
        return {
            1: "The static website hints at a production storage account with a similar naming pattern. Try enumerating storage accounts using tools like cloud-enum.",
            2: "The 'website' container in the production storage account has 'container' access level — you can list its blobs. Look for a config file.",
            3: "config.cfg reveals the URL of a second container. That container uses 'blob' access; construct the direct URL to flag.txt and fetch it.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{St0r4g3_Acc0unt_4cc355}"

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
