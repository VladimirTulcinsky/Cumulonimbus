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
            4: "Membership of cred-administrators grants 'Key Vault Secrets User' on the lab's Key Vault. Sign back in as your user, then read the flag: az keyvault secret show --vault-name <vault> --name flag --query value -o tsv. (Group membership can take a few minutes to take effect; sign out/in to refresh your token.)",
        }

    def get_flag(self):
        return "CUMULONIMBUS{SP_0wn3rsh1p_T0_K3yV4ult_Acc3ss}"

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
              With an administrator account you should remove this user from the owners of the application registration.
              """)
        print(f""" [5] A Key Vault has been created: {output["key_vault_name"]["value"]}. Its 'flag' secret is readable only by members of the group {output["admin_group"]["value"]}.""")
        print(
            f"""Goal: escalate by adding {output["user_name"]["value"]} to the group {output["admin_group"]["value"]}, then read the flag from the Key Vault.
            The group holds no directory role (e.g. Global Administrator) — that would need an Entra ID P1 license — but it IS granted the 'Key Vault Secrets User' RBAC role on {output["key_vault_name"]["value"]}. RBAC roles on a group are a realistic, license-free way for group membership to carry real privilege.
            Once you are a member, sign back in as your user and run: az keyvault secret show --vault-name {output["key_vault_name"]["value"]} --name flag --query value -o tsv
            (The other account in the group is just there to satisfy the owner requirement.)""")
        self.print_mitre_ttps()