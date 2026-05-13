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
            1: "Real-world storage accounts follow environment naming patterns. Use cloud_enum (https://github.com/initstring/cloud_enum) to discover them: ./cloud_enum.py -k cumulonimbusXXXXprd --disable-aws --disable-gcp. Also try other suffixes: dev, tst, uat, stg.",
            2: "The 'website' container in the production storage account has 'container' access level — you can list its blobs. Look for a config file.",
            3: "config.cfg reveals the URL of a second container. That container uses 'blob' access; construct the direct URL to flag.txt and fetch it.",
        }

    def get_flag(self):
        return "CUMULONIMBUS{St0r4g3_Acc0unt_4cc355}"

    def pretty_print_tf_output(self, app_id, output):
        if not output:
            return
        cid = str(output["cumulonimbus_id"]["value"])
        print("###############################################")
        print("#             Required Information            #")
        print("###############################################")
        print(f"[1] Entrypoint (static website): {output['primary_web_endpoint']['value']}")
        print(f"[2] Unique ID  : {cid}")
        print()
        print("Enumerate storage accounts with cloud_enum (https://github.com/initstring/cloud_enum):")
        print(f"  ./cloud_enum.py -k cumulonimbus{cid}prd --disable-aws --disable-gcp")
        print(f"  # Also try other environments: dev, tst, uat, stg")
        print(f"  # e.g. ./cloud_enum.py -k cumulonimbus{cid}dev --disable-aws --disable-gcp")
