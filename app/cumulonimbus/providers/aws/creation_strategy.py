from python_terraform import *
from .utils import get_path_to_aws_app, pretty_print_tf_output
import cumulonimbus.global_variables as global_variables

from cumulonimbus.providers.base.creation_strategy import CreationStrategy, CreationException
from cumulonimbus.providers.base.application_configuration_factory import get_application_configuration


class AWSCreationStrategy(CreationStrategy):
    """
    Implements creation for the AWS provider
    """

    def create(self,
               app_id,
               credentials,
               **kwargs):

        try:
            # Configure application
            application_configuration = get_application_configuration(
                'aws', app_id)
            application_configuration.configure_application()

            # Get absolute path to the terraform directory
            cwd = get_path_to_aws_app(app_id)
            tf = Terraform(working_dir=cwd)
            # return_code, stdout, stderr = tf.init(capture_output=False)
            no_prompt = {"auto-approve": True}

            # return_code, stdout, stderr = tf.apply(skip_plan=True, **no_prompt, no_color=IsFlagged, capture_output=False, refresh=False,
            #                                        var={'shared_credentials_files': global_variables.PATH_TO_AWS_CREDENTIALS, 'shared_config_files': global_variables.PATH_TO_AWS_CREDENTIALS, 'attacker_public_ip': global_variables.ATTACKER_PUBLIC_IP['aws']']})
            # if stderr:
            #     print("Are you sure you have the correct AWS credentials?")
            #     raise CreationException(stderr)

            outputs = tf.output()
            application_configuration.pretty_print_tf_output(app_id, outputs)

            ####
            # # # TODO: delete after test
            return_code, stdout, stderr = tf.destroy(
                capture_output=False, **no_prompt, force=None, var={'shared_credentials_files': global_variables.PATH_TO_AWS_CREDENTIALS})
            ####

        except Exception as e:
            raise CreationException(e)
