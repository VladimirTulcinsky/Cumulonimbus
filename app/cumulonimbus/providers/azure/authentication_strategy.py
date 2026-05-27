import logging
import os

from azure.identity import ClientSecretCredential
import cumulonimbus.global_variables as global_variables
from cumulonimbus.providers.base.authentication_strategy import AuthenticationStrategy, AuthenticationException


class AzureCredentials:

    def __init__(self,
                 client_id=None, client_secret=None,
                 tenant_id=None, subscription_id=None):

        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_context = subscription_id


class AzureAuthenticationStrategy(AuthenticationStrategy):

    def authenticate(self,
                     service_principal=None,
                     tenant_id=None,
                     subscription_id=None,
                     client_id=None, client_secret=None,
                     tenant_domain=None,
                     region='West Europe',
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
            credentials.get_token("https://management.azure.com/.default")

            self.write_credentials_to_file(
                client_id, client_secret, tenant_id, subscription_id, tenant_domain, region)

            return AzureCredentials(client_id, client_secret, tenant_id, subscription_id)

        except Exception as e:
            raise AuthenticationException(e)

    def get_credentials(self):
        missing = [k for k in ("AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID") if not os.environ.get(k)]
        if missing:
            print(f"No Azure credentials found. Please authenticate first: cnimbus azure authenticate ...")
            return None
        return AzureCredentials(
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
            tenant_id=os.environ["AZURE_TENANT_ID"],
            subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        )

    def get_tenant_domain(self):
        return os.environ.get("AZURE_TENANT_DOMAIN", "")

    def get_location(self):
        return os.environ.get("AZURE_LOCATION", "West Europe")

    def write_credentials_to_file(self, client_id, client_secret, tenant_id, subscription_id, tenant_domain=None, location='West Europe'):
        with open(global_variables.PATH_TO_AZURE_CREDENTIALS, "w") as f:
            f.write("AZURE_CLIENT_ID=" + str(client_id or '') + "\n")
            f.write("AZURE_CLIENT_SECRET=" + str(client_secret or '') + "\n")
            f.write("AZURE_TENANT_ID=" + str(tenant_id or '') + "\n")
            f.write("AZURE_SUBSCRIPTION_ID=" + str(subscription_id or '') + "\n")
            f.write("AZURE_TENANT_DOMAIN=" + str(tenant_domain or '') + "\n")
            f.write("AZURE_LOCATION=" + str(location or 'West Europe') + "\n")
