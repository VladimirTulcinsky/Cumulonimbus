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
            1: "Start the o365-attack-toolkit container and configure template.conf with the application ID and secret output by the lab. The tool generates a phishing URL.",
            2: "Visit http://127.0.0.1:8080/ and copy the phishing link. Open it in a browser and sign in as the admin user with the provided credentials to simulate consent being granted.",
            3: "After consent, your redirect URI receives an authorization code. The toolkit exchanges it for tokens stored in a SQLite DB. Dump them with sqlite3 and use the access token to call the Graph API.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{1ll1c1t_C0ns3nt_Gr4nt3d}"

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
        print(
            "This application has not been tested on Windows, better use Linux ;)")
        print("!!! You might need to delete your msal_token_cache.json file !!!")
        print("[1] This is your primary domain: " +
              output["domain_name"]["value"])
        print("[2] This is the global admin that will be responsible for granting admin consent: " +
              output["user_name"]["value"])
        print("[3] The password for the admin is: " +
              output["user_password"]["value"])
        print(
            "[4] Run the following command: docker pull cumulonimbuscloud/o365-attack-toolkit")
        print("[5] Run the following command: docker run --network='host' -v /tmp:/tmp -it --entrypoint /bin/bash cumulonimbuscloud/o365-attack-toolkit:latest")
        print(
            "[6] Run the following command in /go/src/o-365-toolkit: cat > template.conf")
        print("""[7] Paste the following content in the file:
            [server]
            host = 127.0.0.1
            externalport = 30662
            internalport = 8080


            [oauth]
            clientid = "<Application ID of the application you just created>"
            clientsecret = "<Secret of the application you just created>"
            scope = "<The OAuth scopes you want to request to your victim e.g. offline_access contacts.read user.read mail.read mail.send files.readWrite.all files.read files.read.all openid profile AppRoleAssignment.ReadWrite.All>"
            redirecturi = "http://localhost:30662/gettoken" 
            """)
