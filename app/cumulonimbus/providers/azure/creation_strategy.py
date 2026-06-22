from python_terraform import *
import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
from .utils import get_path_to_azure_app
import os
import shutil

from cumulonimbus.providers.base.creation_strategy import CreationStrategy, CreationException
from cumulonimbus.providers.base.application_configuration_factory import get_application_configuration


class AzureCreationStrategy(CreationStrategy):
    """
    Implements creation for the Azure provider
    """

    def create(self,
               app_id,
               credentials,
               **kwargs):

        try:
            # Configure application
            application_configuration = get_application_configuration(
                'azure', app_id)
            application_configuration.configure_application()

            # Get absolute path to the terraform directory
            cwd = get_path_to_azure_app(app_id)
            tf = Terraform(working_dir=cwd)
            return_code, stdout, stderr = tf.init(capture_output=False)
            if return_code != 0:
                raise CreationException(
                    f"terraform init failed (exit code {return_code}). See the Terraform output above.")

            no_prompt = {"auto-approve": True}
            location = os.environ.get('AZURE_LOCATION', 'West Europe')
            name_suffix = cumulonimbus_utils.get_name_suffix()
            return_code, stdout, stderr = tf.apply(skip_plan=True, **no_prompt, no_color=IsFlagged, capture_output=False,
                                                   var={'client_id': os.environ['AZURE_CLIENT_ID'], 'client_secret': os.environ['AZURE_CLIENT_SECRET'], 'tenant_id': os.environ['AZURE_TENANT_ID'], 'subscription_id': os.environ['AZURE_SUBSCRIPTION_ID'], 'attacker_public_ip': global_variables.ATTACKER_PUBLIC_IP['azure'], 'tenant_domain': os.environ.get('AZURE_TENANT_DOMAIN', ''), 'location': location, 'name_suffix': name_suffix})

            if return_code != 0:
                print("The deployment failed. Check the Terraform output above, and that your Azure credentials and permissions are correct.")
                raise CreationException(
                    f"terraform apply failed (exit code {return_code}).")

            outputs = tf.output()
            application_configuration.pretty_print_tf_output(app_id, outputs)

        except Exception as e:
            raise CreationException(e)

    def destroy(self,
                app_id,
                credentials,
                **kwargs):

        try:
            cwd = get_path_to_azure_app(app_id)
            tf = Terraform(working_dir=cwd)
            no_prompt = {"auto-approve": True}
            location = os.environ.get('AZURE_LOCATION', 'West Europe')
            name_suffix = cumulonimbus_utils.get_name_suffix()
            return_code, stdout, stderr = tf.destroy(
                capture_output=False, **no_prompt, force=None, var={'client_id': os.environ['AZURE_CLIENT_ID'], 'client_secret': os.environ['AZURE_CLIENT_SECRET'], 'tenant_id': os.environ['AZURE_TENANT_ID'], 'subscription_id': os.environ['AZURE_SUBSCRIPTION_ID'], 'tenant_domain': os.environ.get('AZURE_TENANT_DOMAIN', ''), 'location': location, 'name_suffix': name_suffix})

            if return_code != 0:
                # Leave the local state in place so the user can retry destroy;
                # deleting it now would orphan any resources that still exist.
                print("The destroy failed. Check the Terraform output above; the lab's state was kept so you can retry.")
                raise CreationException(
                    f"terraform destroy failed (exit code {return_code}).")

            print(f"Successfully destroyed Azure application: {app_id}")
            _cleanup_terraform_state(cwd)

        except Exception as e:
            raise CreationException(e)


def _cleanup_terraform_state(cwd):
    for name in (".terraform", "terraform.tfstate", "terraform.tfstate.backup"):
        path = os.path.join(cwd, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

