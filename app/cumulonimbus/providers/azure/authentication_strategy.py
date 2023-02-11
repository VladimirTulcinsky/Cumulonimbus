import logging
import os

from azure.identity import ClientSecretCredential
from cumulonimbus.providers.base.authentication_strategy import AuthenticationStrategy, AuthenticationException


class AzureCredentials:

    def __init__(self,
                 client_id=None, client_secret=None,
                 tenant_id=None, subscription_context=None):

        self.client_id = client_id,
        self.client_secret = client_secret,
        self.tenant_id = tenant_id
        self.subscription_context = subscription_context
        self.path_to_azure_credentials = os.environ['AZURE_CREDENTIALS_FILE'] if 'AZURE_CREDENTIALS_FILE' in os.environ else os.path.expanduser(
            "~/.azure/credentials")


class AzureAuthenticationStrategy(AuthenticationStrategy):

    def authenticate(self,
                     service_principal=None,
                     tenant_id=None,
                     subscription_context=None,
                     client_id=None, client_secret=None,
                     **kargs):
        """
        Implements authentication for Azure 
        """
        try:

            # Reduce verbosity of logging
            logging.getLogger('azure.identity').setLevel(logging.ERROR)
            logging.getLogger('azure.core.pipeline').setLevel(logging.ERROR)

            # Currently only allowing service principal authentication with client secret
            if service_principal:

                if not tenant_id:
                    raise AuthenticationException('No Tenant ID set')

                if not client_id:
                    raise AuthenticationException('No Client ID set')

                if not client_secret:
                    raise AuthenticationException('No Client Secret set')

                credentials = ClientSecretCredential(
                    client_id=client_id,
                    client_secret=client_secret,
                    tenant_id=tenant_id
                )

            else:
                raise AuthenticationException('Unknown authentication method')

            # Try getting token to authenticate, if error trigger AuthenticationException
            credentials.get_token(
                "https://management.core.windows.net/.default")

            return AzureCredentials(client_id, client_secret, tenant_id, subscription_context)

        except Exception as e:
            raise AuthenticationException(e)

    # def write_credentials_to_file(self, aws_access_key_id, aws_secret_access_key, aws_session_token, region):

    #     f = open(self.path_to_aws_credentials, "w")
    #     f.write("[default]\n")
    #     f.write("aws_access_key_id = " +
    #             str(aws_access_key_id or '') + "\n")
    #     f.write("aws_secret_access_key = " +
    #             str(aws_secret_access_key or '') + "\n")
    #     if aws_session_token:
    #         f.write("aws_session_token = " + aws_session_token + "\n")
    #     f.close()

    #     f = open(self.path_to_aws_config, "w")
    #     f.write("[default]\n")
    #     f.write("region = " + region)
    #     f.close()
