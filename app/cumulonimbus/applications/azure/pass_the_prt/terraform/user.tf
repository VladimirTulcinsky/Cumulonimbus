locals {
  victim_upn = "ptp-victim-${random_id.suffix.hex}@${var.tenant_domain}"
}

resource "azuread_user" "victim" {
  user_principal_name   = local.victim_upn
  display_name          = "PTP Victim ${random_id.suffix.hex}"
  password              = random_password.victim.result
  force_password_change = false

  # Destroy order: Terraform deletes this user first, and only then does the
  # Graph cleanup below run. The other way round, the cleanup deleted the user
  # first and the azuread provider failed on destroy with "User was not found".
  depends_on = [null_resource.victim_user_cleanup]
}

# Allows the victim to RDP into the Azure AD-joined VM using their Entra credentials.
# When they sign in, CloudAP issues a PRT that is stored in LSASS.
resource "azurerm_role_assignment" "victim_vm_login" {
  scope                = azurerm_windows_virtual_machine.ptp.id
  role_definition_name = "Virtual Machine User Login"
  principal_id         = azuread_user.victim.object_id
}

# Safety net: force-delete the Entra ID user via Graph API on destroy, in case
# Terraform's own deletion of azuread_user.victim did not happen. It runs after
# that deletion (see depends_on on the user), so normally it finds nothing and
# prints "User already deleted". The UPN is built from the same inputs rather
# than read from the user, which would create a dependency cycle.
# Uses SP credentials directly so no az CLI authentication is required.
resource "null_resource" "victim_user_cleanup" {
  triggers = {
    upn           = local.victim_upn
    tenant_id     = var.tenant_id
    client_id     = var.client_id
    client_secret = var.client_secret
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<-EOF
      python3 - <<'PYEOF'
import urllib.request, urllib.parse, json, sys

tenant_id     = "${self.triggers.tenant_id}"
client_id     = "${self.triggers.client_id}"
client_secret = "${self.triggers.client_secret}"
upn           = "${self.triggers.upn}"

data = urllib.parse.urlencode({
    "grant_type":    "client_credentials",
    "client_id":     client_id,
    "client_secret": client_secret,
    "scope":         "https://graph.microsoft.com/.default",
}).encode()

req = urllib.request.Request(
    f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
    data=data,
)
with urllib.request.urlopen(req) as r:
    token = json.loads(r.read())["access_token"]

req = urllib.request.Request(
    f"https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(upn)}",
    method="DELETE",
    headers={"Authorization": f"Bearer {token}"},
)
try:
    with urllib.request.urlopen(req):
        print(f"Deleted Entra ID user: {upn}")
except urllib.error.HTTPError as e:
    if e.code == 404:
        print(f"User already deleted: {upn}")
    else:
        print(f"Error deleting user {upn}: HTTP {e.code}", file=sys.stderr)
        sys.exit(1)
PYEOF
    EOF
  }
}
