#!/usr/bin/env python3
"""
One-shot CTFd setup for Cumulonimbus.

Usage:
    python setup.py aws
    python setup.py azure

Optional flags:
    --admin-password   Admin password (default: cumulonimbus)
    --admin-name       Admin username (default: admin)
    --admin-email      Admin e-mail   (default: admin@cumulonimbus.local)
    --ctf-name         Event name     (default: Cumulonimbus — AWS/Azure)
    --timeout          Seconds to wait for CTFd to start (default: 120)

What it does:
  1. Starts the Docker containers for the chosen provider
  2. Waits for CTFd to become ready
  3. Completes the first-run setup wizard
  4. Generates an admin API token
  5. Seeds all matching challenges, flags, tags, and hints
"""

import argparse
import os
import re
import subprocess
import sys
import time

import requests

from seed_challenges import (
    CHALLENGES,
    create_challenge,
    create_flag,
    create_hints,
    create_tags,
    filter_challenges,
    PROVIDER_DEFAULTS,
)

PROVIDER_SERVICES = {
    "aws":   ["ctfd_aws", "db_aws", "cache_aws"],
    "azure": ["ctfd_azure", "db_azure", "cache_azure"],
}

# Directory containing this file (where docker-compose.yml lives)
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

def start_containers(provider: str) -> None:
    services = PROVIDER_SERVICES[provider]
    print(f"  Starting containers: {', '.join(services)} ...", end="", flush=True)
    result = subprocess.run(
        ["docker", "compose", "up", "-d"] + services,
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print()
        print(f"ERROR: docker compose failed:\n{result.stderr}")
        sys.exit(1)
    print(" done.")


# ---------------------------------------------------------------------------
# CTFd helpers
# ---------------------------------------------------------------------------

def _nonce_from_html(html: str) -> str:
    m = re.search(r'name=["\']nonce["\']\s+(?:type=["\']hidden["\']\s+)?value=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    m = re.search(r'value=["\']([^"\']+)["\']\s+name=["\']nonce["\']', html)
    if m:
        return m.group(1)
    raise RuntimeError("Could not find nonce in page HTML")


def _csrf_from_page(session: requests.Session, base_url: str) -> str:
    r = session.get(f"{base_url}/")
    for pat in (
        r"['\"]csrfNonce['\"]\s*:\s*['\"]([a-f0-9]+)['\"]",
        r"csrf[_-]?nonce['\"]?\s*[=:]\s*['\"]([a-f0-9]+)['\"]",
    ):
        m = re.search(pat, r.text, re.IGNORECASE)
        if m:
            return m.group(1)
    if "X-CSRF-Token" in r.headers:
        return r.headers["X-CSRF-Token"]
    raise RuntimeError(
        "Could not extract CSRF nonce from CTFd. "
        "Check that CTFd started correctly and you are logged in."
    )


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def wait_for_ready(base_url: str, timeout: int) -> bool:
    """Poll /setup until CTFd responds.  Returns True if already configured."""
    print(f"  Waiting for CTFd ", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{base_url}/setup", timeout=5, allow_redirects=False)
            if r.status_code == 200:
                print(" ready.")
                return False
            if r.status_code in (301, 302):
                print(" ready (already configured).")
                return True
        except requests.ConnectionError:
            print(".", end="", flush=True)
        time.sleep(2)
    print()
    raise TimeoutError(
        f"CTFd did not become ready within {timeout}s. "
        "Try: docker compose logs ctfd_aws  (or ctfd_azure)"
    )


def run_setup_wizard(
    base_url: str,
    session: requests.Session,
    ctf_name: str,
    admin_name: str,
    admin_email: str,
    admin_password: str,
) -> None:
    print("  Running setup wizard...", end="", flush=True)
    r = session.get(f"{base_url}/setup")
    nonce = _nonce_from_html(r.text)
    r = session.post(
        f"{base_url}/setup",
        data={
            "ctf_name": ctf_name,
            "ctf_description": "Vulnerable-by-design cloud attack scenarios",
            "user_mode": "users",
            "challenge_visibility": "public",
            "account_visibility": "public",
            "score_visibility": "public",
            "registration_visibility": "public",
            "verify_emails": "",
            "team_size": "",
            "name": admin_name,
            "email": admin_email,
            "password": admin_password,
            "nonce": nonce,
        },
        allow_redirects=True,
    )
    if r.status_code >= 400 or "error" in r.text.lower() and "nonce" not in r.text.lower():
        raise RuntimeError(f"Setup wizard failed (HTTP {r.status_code}). Check CTFd logs.")
    print(" done.")


def login(
    base_url: str,
    session: requests.Session,
    admin_name: str,
    admin_password: str,
) -> None:
    print("  Logging in...", end="", flush=True)
    r = session.get(f"{base_url}/login")
    nonce = _nonce_from_html(r.text)
    r = session.post(
        f"{base_url}/login",
        data={"name": admin_name, "password": admin_password, "nonce": nonce},
        allow_redirects=True,
    )
    failed = (
        r.url.rstrip("/").endswith("/login")
        or "incorrect" in r.text.lower()
        or "invalid" in r.text.lower()
    )
    if failed:
        print()
        print(
            f"\nERROR: Login failed for user '{admin_name}'.\n"
            "  Pass your admin password explicitly:\n"
            f"    python setup.py {provider_hint} --admin-password <password>"
        )
        sys.exit(1)
    print(" done.")


def create_api_token(base_url: str, session: requests.Session) -> str:
    print("  Generating API token...", end="", flush=True)
    csrf = _csrf_from_page(session, base_url)
    r = session.post(
        f"{base_url}/api/v1/tokens",
        json={"description": "cumulonimbus-seed", "expiration": None},
        headers={"CSRF-Token": csrf, "Content-Type": "application/json"},
    )
    r.raise_for_status()
    token = r.json()["data"]["value"]
    print(" done.")
    return token


def seed(base_url: str, token: str, provider: str) -> None:
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    r = requests.get(f"{base_url}/api/v1/challenges", headers=headers)
    if r.status_code == 403:
        print("ERROR: Token is invalid or CTFd setup was not completed.")
        sys.exit(1)
    r.raise_for_status()

    existing = {c["name"] for c in r.json().get("data", [])}
    challenges = filter_challenges(provider)

    print(f"\n  Seeding {len(challenges)} challenges:")
    for challenge in challenges:
        if challenge["name"] in existing:
            print(f"    [skip]    {challenge['name']}")
            continue
        cid = create_challenge(base_url, headers, challenge)
        create_flag(base_url, headers, cid, challenge["flag"])
        create_tags(base_url, headers, cid, challenge.get("tags", []))
        create_hints(base_url, headers, cid, challenge.get("hints", []))
        print(f"    [created] {challenge['name']}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

provider_hint = ""   # filled in main() for error messages


def main() -> None:
    global provider_hint

    parser = argparse.ArgumentParser(
        description="Start CTFd and seed Cumulonimbus challenges in one command.",
        usage="python setup.py {aws,azure} [options]",
    )
    parser.add_argument("provider", choices=["aws", "azure"],
                        help="Cloud provider — starts the matching CTFd instance")
    parser.add_argument("--admin-password", default=None, dest="admin_password",
                        help="Admin password (default: 'cumulonimbus' for fresh installs)")
    parser.add_argument("--admin-name", default="admin", dest="admin_name")
    parser.add_argument("--admin-email", default="admin@cumulonimbus.local", dest="admin_email")
    parser.add_argument("--ctf-name", default=None, dest="ctf_name")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Seconds to wait for CTFd to become ready (default: 120)")
    args = parser.parse_args()

    provider_hint = args.provider
    base_url = PROVIDER_DEFAULTS[args.provider]
    ctf_name = args.ctf_name or f"Cumulonimbus — {args.provider.upper()}"
    session = requests.Session()

    print(f"\n=== Cumulonimbus CTFd — {args.provider.upper()} ===\n")

    start_containers(args.provider)
    already_configured = wait_for_ready(base_url, args.timeout)

    if not already_configured:
        password = args.admin_password or "cumulonimbus"
        run_setup_wizard(base_url, session, ctf_name, args.admin_name, args.admin_email, password)
    else:
        if not args.admin_password:
            print(
                "\nERROR: CTFd is already configured. Provide your admin password:\n"
                f"    python setup.py {args.provider} --admin-password <password>"
            )
            sys.exit(1)
        password = args.admin_password
        login(base_url, session, args.admin_name, password)

    token = create_api_token(base_url, session)
    seed(base_url, token, provider=args.provider)

    print(f"\n=== Ready ===")
    print(f"  URL      : {base_url}")
    print(f"  Username : {args.admin_name}")
    print(f"  Password : {password}")


if __name__ == "__main__":
    main()
