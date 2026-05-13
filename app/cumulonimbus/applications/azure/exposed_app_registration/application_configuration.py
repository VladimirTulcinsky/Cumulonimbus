from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    def configure_application(self, **kwargs):
        pass

    def get_difficulty(self):
        return "Intermediate"

    def get_hints(self):
        return {
            1: "A config.json is available at the config blob URL (no auth required). Download it and look for Azure credentials.",
            2: "The JSON contains tenant_id, client_id, and client_secret for an app registration. Use these to authenticate as a service principal: az login --service-principal -u <client_id> -p <client_secret> --tenant <tenant_id>",
            3: "The config also reveals the storage account and container name. Once authenticated as the SP, use: az storage blob download --account-name <acct> --container-name secrets --name flag.txt --auth-mode login",
        }

    def get_flag(self):
        return "CUMULONIMBUS{3xp0s3d_4pp_R3g_Cl13nt_S3cr3t}"

    def pretty_print_tf_output(self, app_id, output):
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Config blob URL     : " + output["config_blob_url"]["value"])
        print("[2] Config storage acct : " + output["storage_account_name"]["value"])
        print("[3] Flag storage acct   : " + output["flag_storage_account"]["value"])
        print("[4] Resource group      : " + output["resource_group_name"]["value"])
        print("")
        print("Start by downloading the public config file:")
        print("  curl -s '{}' | python3 -m json.tool".format(output["config_blob_url"]["value"]))
