from cumulonimbus.providers.base.application_configuration import ApplicationConfigurationAbstract


class ApplicationConfiguration(ApplicationConfigurationAbstract):
    mitre_ttps = [
        {"id": "T1552.001", "name": "Unsecured Credentials: Credentials in Files", "url": "https://attack.mitre.org/techniques/T1552/001/"},
        {"id": "T1530", "name": "Data from Cloud Storage", "url": "https://attack.mitre.org/techniques/T1530/"},
        {"id": "T1619", "name": "Cloud Storage Object Discovery", "url": "https://attack.mitre.org/techniques/T1619/"},
    ]
    def configure_application(self, **kwargs):
        pass
    def get_hints(self):
        return {
            1: "The storage account name starts with 'cmlnmbstfstate'. Try listing blobs in the 'tfstate' container anonymously — no credentials needed if public access is enabled.",
            2: "Download the state file: curl -o tf.json '<state_blob_url>' then inspect it with: cat tf.json | python3 -m json.tool",
            3: "Look inside .outputs in the JSON. All outputs are stored as plaintext regardless of sensitive=true. Find service_principal_client_secret.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{TF_St4t3_S3ns1t1v3_1s_N0t_3ncrypt3d}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print("[1] Storage account : " + output["storage_account_name"]["value"])
        print("[2] State blob URL  : " + output["state_blob_url"]["value"])
        print("[3] Resource group  : " + output["resource_group_name"]["value"])
        print("")
        print("Retrieve the state file directly (no credentials required):")
        print("  curl -o terraform.tfstate '{}'".format(output["state_blob_url"]["value"]))
        print("  cat terraform.tfstate | python3 -m json.tool | grep -A3 'sensitive'")
        self.print_mitre_ttps()