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
            credentials.get_token("https://management.azure.com/.default")

            if not tenant_domain:
                tenant_domain = self._resolve_tenant_domain(credentials, tenant_id)

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

    def _resolve_tenant_domain(self, credentials, tenant_id: str) -> str:
        """Look up the tenant's default domain. Tries multiple APIs in order."""
        domain = self._domain_from_mgmt(credentials, tenant_id)
        if not domain:
            domain = self._domain_from_graph_organization(credentials)
        if not domain:
            domain = self._domain_from_graph_domains(credentials)
        if domain:
            print(f"  Resolved tenant domain: {domain}")
        else:
            print("  WARNING: could not resolve tenant domain automatically.")
            print("  Pass it explicitly: cnimbus azure authenticate ... --tenant-domain <domain>")
            print("  Where to find it: Azure Portal > Microsoft Entra ID > Overview > 'Primary domain'")
            print("  To enable auto-discovery: grant 'Domain.Read.All' (Application) to your service principal")
            print("    Portal: App registrations > <your app> > API permissions > Add > Microsoft Graph > Application > Domain.Read.All > Grant admin consent")
        return domain

    def _domain_from_mgmt(self, credentials, tenant_id: str) -> str:
        try:
            token = credentials.get_token("https://management.azure.com/.default").token
            r = requests.get(
                "https://management.azure.com/tenants?api-version=2022-12-01",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            r.raise_for_status()
            tenants = r.json().get("value", [])
            for tenant in tenants:
                if tenant.get("tenantId", "").lower() == tenant_id.lower():
                    domain = tenant.get("defaultDomain") or next(iter(tenant.get("domains", [])), "")
                    if domain:
                        return domain
                    return ""  # tenant found but ARM strips domain fields for SP tokens
        except Exception as e:
            print(f"  [debug] mgmt /tenants failed: {e}")
        return ""

    def _domain_from_graph_organization(self, credentials) -> str:
        try:
            token = credentials.get_token("https://graph.microsoft.com/.default").token
            r = requests.get(
                "https://graph.microsoft.com/v1.0/organization?$select=verifiedDomains",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            r.raise_for_status()
            for org in r.json().get("value", []):
                for domain in org.get("verifiedDomains", []):
                    if domain.get("isDefault"):
                        return domain.get("name", "")
        except Exception as e:
            print(f"  [debug] graph /organization failed: {e}")
        return ""

    def _domain_from_graph_domains(self, credentials) -> str:
        try:
            token = credentials.get_token("https://graph.microsoft.com/.default").token
            r = requests.get(
                "https://graph.microsoft.com/v1.0/domains?$select=id,isDefault,isInitial",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            r.raise_for_status()
            domains = r.json().get("value", [])
            default = next((d["id"] for d in domains if d.get("isDefault")), None)
            if default:
                return default
            initial = next((d["id"] for d in domains if d.get("isInitial")), None)
            if initial:
                return initial
        except Exception as e:
            print(f"  [debug] graph /domains failed: {e}")
        return ""

    def write_credentials_to_file(self, client_id, client_secret, tenant_id, subscription_id, tenant_domain=None):
        f = open(global_variables.PATH_TO_AZURE_CREDENTIALS, "w")
        f.write("AZURE_CLIENT_ID=" + str(client_id or '') + "\n")
        f.write("AZURE_CLIENT_SECRET=" + str(client_secret or '') + "\n")
        f.write("AZURE_TENANT_ID=" + str(tenant_id or '') + "\n")
        f.write("AZURE_SUBSCRIPTION_ID=" + str(subscription_id or '') + "\n")
        f.write("AZURE_TENANT_DOMAIN=" + str(tenant_domain or '') + "\n")
        f.close()
