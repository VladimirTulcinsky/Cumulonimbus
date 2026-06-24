import json
import os
import uuid

import requests
from azure.identity import ManagedIdentityCredential
from flask import Flask, jsonify, request

app = Flask(__name__)

# Map of flag -> {label, scope, roleDefinitionId}. Injected as a SECURE env var
# so it is never returned by the ARM control plane (a player with Reader must
# not be able to read the flags off the container and skip ahead).
UNLOCKS = json.loads(os.environ.get("UNLOCKS_JSON", "{}"))
PRINCIPAL_ID = os.environ["ATTACKER_PRINCIPAL_ID"]
MI_CLIENT_ID = os.environ.get("MI_CLIENT_ID") or None
ARM = "https://management.azure.com"

_cred = ManagedIdentityCredential(client_id=MI_CLIENT_ID) if MI_CLIENT_ID else ManagedIdentityCredential()


def _arm_token():
    return _cred.get_token(f"{ARM}/.default").token


def _extract_flag():
    if request.is_json:
        return (request.get_json(silent=True) or {}).get("flag", "")
    return request.form.get("flag") or request.args.get("flag") or ""


@app.route("/")
def index():
    body = (
        "Cumulonimbus Gatekeeper\n"
        "=======================\n"
        "Submit a flag you have found to unlock the next level of access:\n\n"
        "  curl -s -X POST <this-url>/unlock \\\n"
        "       -H 'Content-Type: application/json' \\\n"
        "       -d '{\"flag\":\"CUMULONIMBUS{...}\"}'\n\n"
        "A correct flag grants your account a new Azure role. RBAC takes a\n"
        "minute or two to propagate before the new access works.\n"
    )
    return body, 200, {"Content-Type": "text/plain"}


@app.route("/unlock", methods=["POST", "GET"])
def unlock():
    flag = (_extract_flag() or "").strip()
    entry = UNLOCKS.get(flag)
    if not entry:
        return jsonify({"status": "denied", "message": "Incorrect or unknown flag."}), 403

    try:
        token = _arm_token()
    except Exception as exc:  # noqa: BLE001
        return jsonify({"status": "error", "message": f"token acquisition failed: {exc}"}), 500

    ra_id = str(uuid.uuid4())
    url = (
        f"{ARM}{entry['scope']}/providers/Microsoft.Authorization/"
        f"roleAssignments/{ra_id}?api-version=2022-04-01"
    )
    payload = {
        "properties": {
            "roleDefinitionId": entry["roleDefinitionId"],
            "principalId": PRINCIPAL_ID,
            "principalType": "User",
        }
    }
    resp = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        return jsonify(
            {
                "status": "granted",
                "unlocked": entry["label"],
                "note": "Access granted. RBAC can take 1-2 minutes to propagate before it works.",
            }
        )
    if resp.status_code == 409 or "RoleAssignmentExists" in resp.text:
        return jsonify({"status": "already-granted", "unlocked": entry["label"]})
    return jsonify({"status": "error", "code": resp.status_code, "detail": resp.text[:500]}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
