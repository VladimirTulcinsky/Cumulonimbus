import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

# Map of flag -> {label, scope, role}. Injected as a SECURE env var so the flags
# are never returned by the ARM control plane.
UNLOCKS = json.loads(os.environ.get("UNLOCKS_JSON", "{}"))
PRINCIPAL_ID = os.environ["ATTACKER_PRINCIPAL_ID"]
MI_CLIENT_ID = os.environ.get("MI_CLIENT_ID", "")


def _az(args):
    return subprocess.run(
        ["az"] + args + ["--only-show-errors", "-o", "json"],
        capture_output=True, text=True,
    )


def _login():
    cmd = ["login", "--identity"]
    if MI_CLIENT_ID:
        cmd += ["--username", MI_CLIENT_ID]
    return _az(cmd)


def _grant_one(role, scope):
    args = [
        "role", "assignment", "create",
        "--assignee-object-id", PRINCIPAL_ID,
        "--assignee-principal-type", "User",
        "--role", role,
        "--scope", scope,
    ]
    res = _az(args)
    out = (res.stderr or "") + (res.stdout or "")
    if res.returncode == 0:
        return "granted", ""
    if "already exists" in out.lower() or "RoleAssignmentExists" in out:
        return "already-granted", ""
    # Token may have lapsed — re-login once and retry.
    _login()
    res = _az(args)
    out = (res.stderr or "") + (res.stdout or "")
    if res.returncode == 0:
        return "granted", ""
    if "already exists" in out.lower() or "RoleAssignmentExists" in out:
        return "already-granted", ""
    return "error", out[:500]


def _grant(entry):
    # An unlock may grant one or more roles (all scoped to the same resource).
    roles = entry.get("roles") or ([entry["role"]] if entry.get("role") else [])
    statuses = []
    for role in roles:
        status, detail = _grant_one(role, entry["scope"])
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
            except Exception:
                flag = parse_qs(raw).get("flag", [""])[0]
        flag = (flag or "").strip()

        entry = UNLOCKS.get(flag)
        if not entry:
            self._send(403, {"status": "denied", "message": "Incorrect or unknown flag."})
            return

        status, detail = _grant(entry)
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
    _login()
    ThreadingHTTPServer(("0.0.0.0", 80), Handler).serve_forever()
