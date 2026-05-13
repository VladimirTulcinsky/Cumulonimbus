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
            1: "After device code phishing, your refresh token is in msal_token_cache.json. A Family Refresh Token can be redeemed by any FOCI client — you are not limited to the Azure CLI client ID.",
            2: "Use TokenTactics or a manual token request to exchange the refresh token using a different client_id, e.g. Microsoft Office (d3590ed6-52b3-4102-aeff-aad2292ab01c).",
            3: "With the new token (scoped to a client that has Group.ReadWrite.All), call the Microsoft Graph API to add your user to the administrators group: POST /v1.0/groups/<id>/members/$ref",
        }

    def get_flag(self):
        return "CUMULONIMBUS{F4m1ly_R3fr3sh_T0k3n_4bus3d}"

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
        print(
            "This application has not been tested on Windows, better use Linux ;)")
        print("!!! You might need to delete your msal_token_cache.json file !!!")
        print("[1] This is your primary domain: " +
              output["domain_name"]["value"])
        print("""In this application you will have to simulate device code phishing.Instead of setting up an phishing application that will refresh the code to avoid the device code to expire we will directly use the code when our victim logs in""")
        print("[2] run az login --use-device-code --allow-no-subscriptions, copy the code, go to https://microsoft.com/devicelogin and paste the code.")
        print("[3] Log in with this user: " +
              output["user_name"]["value"])
        print("[4] The password is: " +
              output["user_password"]["value"])
        print(
            f"""Hint: Now the goal is to escalate your privileges to global admin by adding {output["user_name"]["value"]} to the groups of administrators". Note that the group has no role assignments (e.g. global admin) as this required a P1 license, in a real world scenario this is very likely to occur""")
