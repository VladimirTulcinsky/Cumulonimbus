from python_terraform import *
import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
from .utils import get_path_to_azure_app
import os
import shutil
import subprocess

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

            # Some labs grant admin consent via `az` in a Terraform local-exec.
            # The az CLI keeps its own session (separate from the Python SDK auth
            # Cumulonimbus uses), so log it in with the same service principal
            # first, and log out afterwards so it doesn't shadow the player's own
            # `az login` during the lab.
            _az_login()
            try:
                no_prompt = {"auto-approve": True}
                location = os.environ.get('AZURE_LOCATION', 'West Europe')
                name_suffix = cumulonimbus_utils.get_name_suffix()
                return_code, stdout, stderr = tf.apply(skip_plan=True, **no_prompt, no_color=IsFlagged, capture_output=False, refresh=False,
                                                       var={'client_id': os.environ['AZURE_CLIENT_ID'], 'client_secret': os.environ['AZURE_CLIENT_SECRET'], 'tenant_id': os.environ['AZURE_TENANT_ID'], 'subscription_id': os.environ['AZURE_SUBSCRIPTION_ID'], 'attacker_public_ip': global_variables.ATTACKER_PUBLIC_IP['azure'], 'tenant_domain': os.environ.get('AZURE_TENANT_DOMAIN', ''), 'location': location, 'name_suffix': name_suffix})

                if return_code != 0:
                    print("The deployment failed. Check the Terraform output above, and that your Azure credentials and permissions are correct.")
                    raise CreationException(
                        f"terraform apply failed (exit code {return_code}).")

                outputs = tf.output()
                application_configuration.pretty_print_tf_output(app_id, outputs)
            finally:
                _az_logout()

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


def _az_login():
    """Authenticate the `az` CLI with the configured service principal so that
    lab Terraform local-exec steps that call `az` (e.g. admin consent) work."""
    try:
        subprocess.run(
            ["az", "login", "--service-principal",
             "-u", os.environ["AZURE_CLIENT_ID"],
             "-p", os.environ["AZURE_CLIENT_SECRET"],
             "--tenant", os.environ["AZURE_TENANT_ID"],
             "--allow-no-subscriptions"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
    except FileNotFoundError:
        raise CreationException(
            "The Azure CLI (az) is required to deploy Azure labs but was not found on PATH.")
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or "").strip() or "az login failed"
        raise CreationException(f"az login (service principal) failed: {detail}")

    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if subscription_id:
        subprocess.run(["az", "account", "set", "--subscription", subscription_id],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _az_logout():
    """Drop the deploy-time az session so it doesn't shadow the player's own login."""
    subprocess.run(["az", "logout"], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _cleanup_terraform_state(cwd):
    for name in (".terraform", "terraform.tfstate", "terraform.tfstate.backup"):
        path = os.path.join(cwd, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

