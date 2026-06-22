from python_terraform import *
from .utils import get_path_to_aws_app, pretty_print_tf_output
import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
import os
import shutil

from cumulonimbus.providers.base.creation_strategy import CreationStrategy, CreationException
from cumulonimbus.providers.base.application_configuration_factory import get_application_configuration


class AWSCreationStrategy(CreationStrategy):
    """
    Implements creation and destruction for the AWS provider.
    """

    def create(self, app_id, credentials, **kwargs):
        try:
            application_configuration = get_application_configuration('aws', app_id)
            application_configuration.configure_application()

            cwd = get_path_to_aws_app(app_id)
            tf = Terraform(working_dir=cwd)
            return_code, stdout, stderr = tf.init(capture_output=False)
            if return_code != 0:
                raise CreationException(
                    f"terraform init failed (exit code {return_code}). See the Terraform output above.")
            no_prompt = {"auto-approve": True}
            region = getattr(credentials, 'aws_region', 'eu-west-1')
            name_suffix = cumulonimbus_utils.get_name_suffix()
            return_code, stdout, stderr = tf.apply(
                skip_plan=True,
                **no_prompt,
                no_color=IsFlagged,
                capture_output=False,
                refresh=False,
                var={
                    'shared_credentials_files': global_variables.PATH_TO_AWS_CREDENTIALS,
                    'shared_config_files': global_variables.PATH_TO_AWS_CONFIG,
                    'attacker_public_ip': global_variables.ATTACKER_PUBLIC_IP['aws'],
                    'region': region,
                    'name_suffix': name_suffix,
                }
            )

            if return_code != 0:
                print("The deployment failed. Check the Terraform output above, and that your AWS credentials and permissions are correct.")
                raise CreationException(
                    f"terraform apply failed (exit code {return_code}).")

            outputs = tf.output()
            application_configuration.pretty_print_tf_output(app_id, outputs)

        except Exception as e:
            raise CreationException(e)

    def destroy(self, app_id, credentials, **kwargs):
        try:
            application_configuration = get_application_configuration('aws', app_id)

            cwd = get_path_to_aws_app(app_id)
            tf = Terraform(working_dir=cwd)
            no_prompt = {"auto-approve": True}
            region = getattr(credentials, 'aws_region', 'eu-west-1')
            name_suffix = cumulonimbus_utils.get_name_suffix()
            return_code, stdout, stderr = tf.destroy(
                capture_output=False,
                **no_prompt,
                force=None,
                var={
                    'shared_credentials_files': global_variables.PATH_TO_AWS_CREDENTIALS,
                    'shared_config_files': global_variables.PATH_TO_AWS_CONFIG,
                    'region': region,
                    'name_suffix': name_suffix,
                }
            )

            if return_code != 0:
                # Leave the local state in place so the user can retry destroy;
                # deleting it now would orphan any resources that still exist.
                print("The destroy failed. Check the Terraform output above; the lab's state was kept so you can retry.")
                raise CreationException(
                    f"terraform destroy failed (exit code {return_code}).")

            print(f"Successfully destroyed AWS application: {app_id}")
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
