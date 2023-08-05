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
        print("[1] This is your primary domain: " +
              output["domain_name"]["value"])
        print("[2] Log in with this user: " +
              output["user_name"]["value"])
        print("[3] The password is: " +
              output["user_password"]["value"])
        print(f""" [4] An application registration has been created for you with the name: {output["app_registration"]["value"]}. 
              This application has the application permission Group.ReadWrite.All and {output["user_name"]["value"]} is owner on the application registration.
              With an administatror account you should remove this user from the owners of the application registration.
              """)
        print(
            f"""Hint: Now the goal is to escalate your privileges to global admin by adding {output["user_name"]["value"]} to the group {output["admin_group"]["value"]}. 
            Note that the group has no role assignments (e.g. global admin) as this required a P1 license, in a real world scenario this is very likely to occur.
            The other user in the group {output["admin_group"]["value"]} is just a random account because there's a requirement to have at least one owner""")
