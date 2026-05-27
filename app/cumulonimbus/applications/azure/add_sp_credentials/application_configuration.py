from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1098.001", "name": "Additional Cloud Credentials", "url": "https://attack.mitre.org/techniques/T1098/001/"},
        {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "url": "https://attack.mitre.org/techniques/T1078/004/"},
        {"id": "T1098", "name": "Account Manipulation", "url": "https://attack.mitre.org/techniques/T1098/"},
    ]
    def configure_application(self, **kwargs):
        """
        Given parameters, this runs code that is required for each vulnerable application to run correctly.
        """
        pass

    def get_difficulty(self):
        return "Advanced"

    def get_hints(self):
        return {
            1: "The user was removed from the app registration owners, but check whether they still appear as owner on the underlying service principal: az ad sp list --show-mine",
            2: "As a service principal owner you can add new credentials: az ad sp credential reset --id <sp-object-id> --append. Use the new client secret to authenticate as the SP.",
            3: "Authenticate as the SP (which has Group.ReadWrite.All), then add your user to the 'cred-administrators' group: az rest --method POST --uri https://graph.microsoft.com/v1.0/groups/<id>/members/$ref",
        }

    def get_flag(self):
        return "CUMULONIMBUS{SP_Cr3d3nt14ls_4dd3d}"

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
        print(f""" [4] An application registration has been created for you with the name: {output["app_registration"]["value"]}. 
              This application has the application permission Group.ReadWrite.All and {output["user_name"]["value"]} is owner on the application registration.
              With an administatror account you should remove this user from the owners of the application registration.
              """)
        print(
            f"""Hint: Now the goal is to escalate your privileges to global admin by adding {output["user_name"]["value"]} to the group {output["admin_group"]["value"]}. 
            Note that the group has no role assignments (e.g. global admin) as this required a P1 license, in a real world scenario this is very likely to occur.
            The other user in the group {output["admin_group"]["value"]} is just a random account because there's a requirement to have at least one owner""")
        self.print_mitre_ttps()