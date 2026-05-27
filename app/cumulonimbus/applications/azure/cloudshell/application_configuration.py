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
        return "Intermediate"

    def get_hints(self):
        return {
            1: "The storage account has a file share. List the shares and look for the .cloudconsole folder — it contains a Cloud Shell disk image.",
            2: "Download the .img file using azcopy or az storage file download. The file is named acc_<username>.img.",
            3: "Mount the image locally: sudo mount -o loop acc_noher.img /mnt/cs  — then search for the flag inside the mounted filesystem.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{CSStorageMustBeLockedDown}"

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
        print("#             Required Information            #")
        print("###############################################")
        print("[1] This is your primary domain: " +
              output["domain_name"]["value"])
        print("[2] Log in with this user: " +
              output["user_name"]["value"])
        print("[3] The password is: " +
              output["user_password"]["value"])
