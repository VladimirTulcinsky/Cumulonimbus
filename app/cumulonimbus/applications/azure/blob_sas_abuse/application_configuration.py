from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract
import cumulonimbus.core.utils as utils
import os


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Beginner"

    def get_hints(self):
        return {
            1: "Browse to the web app endpoint and view the page source — developers sometimes leave credentials in JavaScript files.",
            2: "The app.js file contains a SAS_TOKEN variable. A SAS token is a query string starting with '?sv=' that grants access to Azure Blob Storage.",
            3: "Use the SAS token to list and read the private 'secrets' container: curl 'https://<account>.blob.core.windows.net/secrets?restype=container&comp=list&<sas_token_without_question_mark>'",
        }

    def get_flag(self):
        return "CUMULONIMBUS{SAS_T0k3n_N3v3r_1n_C0d3}"

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Web app endpoint  : " + output["web_endpoint"]["value"])
        print("[2] app.js URL        : " + output["app_js_url"]["value"])
        print("[3] Storage account   : " + output["storage_account_name"]["value"])
        print("")
        print("Start by browsing to the web endpoint and inspecting app.js.")
