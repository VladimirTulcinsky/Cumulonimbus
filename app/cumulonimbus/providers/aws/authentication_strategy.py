import boto3
import logging
import os
import configparser
import cumulonimbus.global_variables as global_variables

from cumulonimbus.providers.aws.utils import get_caller_identity
from cumulonimbus.providers.base.authentication_strategy import AuthenticationStrategy, AuthenticationException


class AWSCredentials:

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_session_token=None, aws_region="eu-west-1"):
        self.aws_access_key_id = aws_access_key_id,
        self.aws_secret_access_key = aws_secret_access_key,
        self.aws_session_token = aws_session_token,
        self.aws_region = aws_region


class AWSAuthenticationStrategy(AuthenticationStrategy):
    """
    Implements authentication for the AWS provider
    """

    def authenticate(self, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None, region="eu-west-1",
                     **kwargs):

        try:

            # Set logging level to error for libraries as otherwise generates a lot of warnings
            logging.getLogger('botocore').setLevel(logging.ERROR)
            logging.getLogger('botocore.auth').setLevel(logging.ERROR)
            logging.getLogger('urllib3').setLevel(logging.ERROR)

            if aws_access_key_id and aws_secret_access_key:
                if aws_session_token:
                    session = boto3.Session(
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        aws_session_token=aws_session_token,
                    )
                else:
                    session = boto3.Session(
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                    )
            else:
                session = boto3.Session()

            # Test querying for current user
            get_caller_identity(session)

            # Writing credentials to file (container runs as root so permission should not be an issue)
            # TODO: Maybe export to env variables instead?

            self.write_credentials_to_file(
                aws_access_key_id, aws_secret_access_key, aws_session_token, region)

            return AWSCredentials(aws_access_key_id, aws_secret_access_key, aws_session_token, region)

        except Exception as e:
            raise AuthenticationException(e)

    def get_credentials(self):
        print("Getting credentials for AWS")

        session = boto3.Session(profile_name='cumulonimbus')
        credentials = session.get_credentials()
        credentials = self.authenticate(aws_access_key_id=credentials.access_key,
                                        aws_secret_access_key=credentials.secret_key, aws_session_token=credentials.token)
        return credentials

    def write_credentials_to_file(self, aws_access_key_id, aws_secret_access_key, aws_session_token, region):

        f = open(global_variables.PATH_TO_AWS_CREDENTIALS, "w")
        f.write("[cumulonimbus]\n")
        f.write("aws_access_key_id = " +
                str(aws_access_key_id or '') + "\n")
        f.write("aws_secret_access_key = " +
                str(aws_secret_access_key or '') + "\n")
        if aws_session_token:
            f.write("aws_session_token = " + aws_session_token + "\n")
        f.close()

        f = open(global_variables.PATH_TO_AWS_CONFIG, "w")
        f.write("[cumulonimbus]\n")
        f.write("region = " + region)
        f.close()
