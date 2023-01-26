from python_terraform import *
from .utils import get_path_to_aws_app


from cumulonimbus.providers.base.creation_strategy import CreationStrategy, CreationException


class AWSCreationStrategy(CreationStrategy):
    """
    Implements creation for the AWS provider
    """

    def create(self,
               app_id,
               credentials,
               **kwargs):

        try:
            # Get absolute path to the terraform directory
            cwd = get_path_to_aws_app(app_id)
            tf = Terraform(working_dir=cwd)
            # return_code, stdout, stderr = tf.init(capture_output=False)
            no_prompt = {"auto-approve": True}
            # return_code, stdout, stderr = tf.apply(skip_plan=True, **no_prompt, no_color=IsFlagged, capture_output=False, refresh=False,
            #    var={'shared_credentials_file': credentials.path_to_aws_credentials})
            # return_code, stdout, stderr = tf.apply(skip_plan=True, **no_prompt, no_color=IsFlagged, capture_output=False, refresh=False,
            #    var={'shared_credentials_file': credentials.path_to_aws_credentials})
            ####
            # TODO: delete after test
            return_code, stdout, stderr = tf.destroy(
                capture_output=False, **no_prompt, force=None, var={'shared_credentials_file': credentials.path_to_aws_credentials})
            ####

        except Exception as e:
            raise CreationException(e)
