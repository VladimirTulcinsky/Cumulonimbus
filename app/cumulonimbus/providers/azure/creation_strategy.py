from python_terraform import *
import cumulonimbus.global_variables as global_variables
from .utils import get_path_to_azure_app
import os

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
            no_prompt = {"auto-approve": True}
            return_code, stdout, stderr = tf.apply(skip_plan=True, **no_prompt, no_color=IsFlagged, capture_output=False, refresh=False,
                                                   var={'client_id': os.environ['AZURE_CLIENT_ID'], 'client_secret': os.environ['AZURE_CLIENT_SECRET'], 'tenant_id': os.environ['AZURE_TENANT_ID'], 'subscription_id': os.environ['AZURE_SUBSCRIPTION_ID'], 'attacker_public_ip': global_variables.ATTACKER_PUBLIC_IP['azure']})

            if stderr:
                print("Are you sure you have the correct Azure credentials?")
                raise CreationException(stderr)

            outputs = tf.output()
            application_configuration.pretty_print_tf_output(app_id, outputs)

        except Exception as e:
            raise CreationException(e)

# TEST (clean up as lot of duplicate code)
    def destroy(self,
                app_id,
                credentials,
                **kwargs):

        try:
            application_configuration = get_application_configuration(
                'azure', app_id)  # can't this be removed?
            # # Get absolute path to the terraform directory
            cwd = get_path_to_azure_app(app_id)
            tf = Terraform(working_dir=cwd)
            no_prompt = {"auto-approve": True}
            return_code, stdout, stderr = tf.destroy(
                capture_output=False, **no_prompt, force=None, var={'client_id': os.environ['AZURE_CLIENT_ID'], 'client_secret': os.environ['AZURE_CLIENT_SECRET'], 'tenant_id': os.environ['AZURE_TENANT_ID'], 'subscription_id': os.environ['AZURE_SUBSCRIPTION_ID']})

            outputs = tf.output()
            application_configuration.pretty_print_tf_output(app_id, outputs)

            if stderr:
                print("Are you sure you have the correct Azure credentials?")
                raise CreationException(stderr)

        except Exception as e:
            raise CreationException(e)

# TEST
