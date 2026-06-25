import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Map of flag -> {label, scope, roles:[guid,...]}. Injected as a SECURE env var
# so the flags are never returned by the ARM control plane.
UNLOCKS = json.loads(os.environ.get("UNLOCKS_JSON", "{}"))
PRINCIPAL_ID = os.environ["ATTACKER_PRINCIPAL_ID"]
MI_CLIENT_ID = os.environ.get("MI_CLIENT_ID", "")

ARM = "https://management.azure.com"
RESOURCE = "https://management.azure.com/"


def _http(method, url, headers=None, data=None, timeout=20):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def get_token():
    """Fetch an ARM token from the container's managed identity.

    Tries the App Service-style IDENTITY_ENDPOINT first (set on some hosts),
    then falls back to the IMDS endpoint used by VMs / AKS / ACI. Raises with a
    detailed message if both fail, so the cause is visible in the HTTP response.
    """
    errors = []

    endpoint = os.environ.get("IDENTITY_ENDPOINT")
    header = os.environ.get("IDENTITY_HEADER")
    if endpoint and header:
        params = {"resource": RESOURCE, "api-version": "2019-08-01"}
        if MI_CLIENT_ID:
            params["client_id"] = MI_CLIENT_ID
        url = endpoint + "?" + urllib.parse.urlencode(params)
        try:
            code, body = _http("GET", url, {"X-IDENTITY-HEADER": header})
            if code == 200:
                return json.loads(body)["access_token"]
            errors.append("IDENTITY_ENDPOINT %s: %s" % (code, body[:200]))
        except Exception as exc:  # noqa: BLE001
            errors.append("IDENTITY_ENDPOINT error: %s" % exc)

    params = {"resource": RESOURCE, "api-version": "2018-02-01"}
    if MI_CLIENT_ID:
        params["client_id"] = MI_CLIENT_ID
    url = "http://169.254.169.254/metadata/identity/oauth2/token?" + urllib.parse.urlencode(params)
    try:
        code, body = _http("GET", url, {"Metadata": "true"})
        if code == 200:
            return json.loads(body)["access_token"]
        errors.append("IMDS %s: %s" % (code, body[:200]))
    except Exception as exc:  # noqa: BLE001
        errors.append("IMDS error: %s" % exc)

    raise RuntimeError("token acquisition failed: " + "; ".join(errors))


def _role_definition_id(scope, role_guid):
    match = re.search(r"/subscriptions/([^/]+)/", scope)
    subscription = match.group(1) if match else ""
    return "/subscriptions/%s/providers/Microsoft.Authorization/roleDefinitions/%s" % (subscription, role_guid)


def _grant_one(token, role_guid, scope):
    assignment_id = str(uuid.uuid4())
    url = "%s%s/providers/Microsoft.Authorization/roleAssignments/%s?api-version=2022-04-01" % (ARM, scope, assignment_id)
    payload = json.dumps({
        "properties": {
            "roleDefinitionId": _role_definition_id(scope, role_guid),
            "principalId": PRINCIPAL_ID,
            "principalType": "User",
        }
    }).encode()
    code, resp = _http(
        "PUT", url,
        {"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        payload, timeout=30,
    )
    if code in (200, 201):
        return "granted", ""
    if code == 409 or "RoleAssignmentExists" in resp:
        return "already-granted", ""
    return "error", "%s: %s" % (code, resp[:300])


def grant(entry):
    try:
        token = get_token()
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)

    roles = entry.get("roles") or ([entry["role"]] if entry.get("role") else [])
    statuses = []
    for role_guid in roles:
        status, detail = _grant_one(token, role_guid, entry["scope"])
        if status == "error":
            return "error", detail
        statuses.append(status)
    if statuses and all(s == "already-granted" for s in statuses):
        return "already-granted", ""
    return "granted", ""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(200, {
            "service": "Cumulonimbus Gatekeeper",
            "usage": "POST /unlock with JSON {\"flag\": \"CUMULONIMBUS{...}\"}",
            "note": "A correct flag grants your account a real Azure role. RBAC takes 1-2 minutes to propagate.",
        })

    def do_POST(self):
        if not self.path.startswith("/unlock"):
            self._send(404, {"status": "not-found"})
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length).decode() if length else ""
        flag = ""
        if raw:
            try:
                flag = (json.loads(raw) or {}).get("flag", "")
            except Exception:  # noqa: BLE001
                flag = urllib.parse.parse_qs(raw).get("flag", [""])[0]
        flag = (flag or "").strip()

        entry = UNLOCKS.get(flag)
        if not entry:
            self._send(403, {"status": "denied", "message": "Incorrect or unknown flag."})
            return

        status, detail = grant(entry)
        if status == "granted":
            self._send(200, {"status": "granted", "unlocked": entry["label"],
                             "note": "Access granted. RBAC can take 1-2 minutes to propagate before it works."})
        elif status == "already-granted":
            self._send(200, {"status": "already-granted", "unlocked": entry["label"]})
        else:
            self._send(502, {"status": "error", "detail": detail})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 80), Handler).serve_forever()
