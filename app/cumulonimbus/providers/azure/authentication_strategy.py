import logging
import os

import requests
from azure.identity import ClientSecretCredential
import cumulonimbus.global_variables as global_variables
from cumulonimbus.providers.base.authentication_strategy import AuthenticationStrategy, AuthenticationException


class AzureCredentials:

    def __init__(self,
                 client_id=None, client_secret=None,
                 tenant_id=None, subscription_id=None):

        self.client_id = client_id,
        self.client_secret = client_secret,
        self.tenant_id = tenant_id
        self.subscription_context = subscription_id


class AzureAuthenticationStrategy(AuthenticationStrategy):

    def authenticate(self,
                     service_principal=None,
                     tenant_id=None,
                     subscription_id=None,
                     client_id=None, client_secret=None,
                     tenant_domain=None,
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
            token = credentials.get_token("https://management.azure.com/.default")

            if not tenant_domain:
                tenant_domain = self._resolve_tenant_domain(token.token, tenant_id)

            self.write_credentials_to_file(
                client_id, client_secret, tenant_id, subscription_id, tenant_domain)

            return AzureCredentials(client_id, client_secret, tenant_id, subscription_id)

        except Exception as e:
            raise AuthenticationException(e)

    def get_credentials(self):
        """
        Returns the credentials object
        """

        print("Getting credentials for Azure")
        try:
            client_id = os.environ["AZURE_CLIENT_ID"]
            client_secret = os.environ["AZURE_CLIENT_SECRET"]
            tenant_id = os.environ["AZURE_TENANT_ID"]
            subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
            credentials = self.authenticate(service_principal=True,
                                            client_id=client_id,
                                            client_secret=client_secret,
                                            tenant_id=tenant_id, subscription_id=subscription_id)
            return credentials
        except KeyError:
            print("Are you sure you are authenticated to Azure and every parameter is set? (client_id, client_secret, tenant_id, subscription_id)")

    def get_tenant_domain(self):
        return os.environ.get("AZURE_TENANT_DOMAIN", "")

    def _resolve_tenant_domain(self, token: str, tenant_id: str) -> str:
        """Look up the tenant's default domain via the management plane (no Graph perms needed)."""
        try:
            r = requests.get(
                "https://management.azure.com/tenants?api-version=2022-12-01",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            r.raise_for_status()
            for tenant in r.json().get("value", []):
                if tenant.get("tenantId") == tenant_id:
                    domain = tenant.get("defaultDomain", "")
                    if domain:
                        print(f"  Resolved tenant domain: {domain}")
                        return domain
        except Exception:
            pass
        return ""

    def write_credentials_to_file(self, client_id, client_secret, tenant_id, subscription_id, tenant_domain=None):
        f = open(global_variables.PATH_TO_AZURE_CREDENTIALS, "w")
        f.write("AZURE_CLIENT_ID=" + str(client_id or '') + "\n")
        f.write("AZURE_CLIENT_SECRET=" + str(client_secret or '') + "\n")
        f.write("AZURE_TENANT_ID=" + str(tenant_id or '') + "\n")
        f.write("AZURE_SUBSCRIPTION_ID=" + str(subscription_id or '') + "\n")
        f.write("AZURE_TENANT_DOMAIN=" + str(tenant_domain or '') + "\n")
        f.close()
