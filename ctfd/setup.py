#!/usr/bin/env python3
"""
One-shot CTFd initialiser for Cumulonimbus.

Usage (from the ctfd/ directory):
    docker compose up -d
    python setup.py

Optional flags:
    --url              CTFd base URL          (default: http://localhost:8000)
    --ctf-name         Event name             (default: Cumulonimbus)
    --admin-name       Admin username         (default: admin)
    --admin-email      Admin e-mail           (default: admin@cumulonimbus.local)
    --admin-password   Admin password         (default: cumulonimbus)
    --timeout          Seconds to wait for CTFd to start (default: 120)

What it does:
  1. Polls CTFd until it is accepting connections
  2. Completes the first-run setup wizard
  3. Logs in and mints an admin API token
  4. Seeds all Cumulonimbus challenges, flags, tags, and hints
"""

import argparse
import re
import sys
import time

import requests

from seed_challenges import CHALLENGES, create_challenge, create_flag, create_hints, create_tags


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nonce_from_html(html: str) -> str:
    """Extract the hidden nonce / CSRF token from a CTFd HTML page."""
    # Setup and login forms embed:  <input name="nonce" value="...">
    m = re.search(r'name=["\']nonce["\']\s+(?:type=["\']hidden["\']\s+)?value=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    # Some versions swap attribute order
    m = re.search(r'value=["\']([^"\']+)["\']\s+name=["\']nonce["\']', html)
    if m:
        return m.group(1)
    raise RuntimeError("Could not find nonce in page HTML")


def _csrf_from_page(session: requests.Session, base_url: str) -> str:
    """Return the CSRF nonce for authenticated API calls."""
    r = session.get(f"{base_url}/")
    # CTFd 3.x embeds:  'csrfNonce': "deadbeef..."
    for pat in (
        r"['\"]csrfNonce['\"]\s*:\s*['\"]([a-f0-9]+)['\"]",
        r"csrf[_-]?nonce['\"]?\s*[=:]\s*['\"]([a-f0-9]+)['\"]",
    ):
        m = re.search(pat, r.text, re.IGNORECASE)
        if m:
            return m.group(1)
    # Fallback: X-CSRF-Token response header (older builds)
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
    """
    Poll /setup until CTFd responds.

    Returns True if CTFd is already configured (redirects away from /setup),
    False if the setup wizard is still waiting.
    """
    print(f"Waiting for CTFd at {base_url} ", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{base_url}/setup", timeout=5, allow_redirects=False)
            if r.status_code == 200:
                print(" ready (setup wizard pending).")
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
        "Is Docker running? Try: docker compose logs ctfd"
    )


def run_setup_wizard(
    base_url: str,
    session: requests.Session,
    ctf_name: str,
    admin_name: str,
    admin_email: str,
    admin_password: str,
) -> None:
    """Complete the CTFd first-run setup wizard."""
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
    """Authenticate the session as the admin user."""
    print("  Logging in...", end="", flush=True)
    r = session.get(f"{base_url}/login")
    nonce = _nonce_from_html(r.text)

    r = session.post(
        f"{base_url}/login",
        data={
            "name": admin_name,
            "password": admin_password,
            "nonce": nonce,
        },
        allow_redirects=True,
    )
    if "/login" in r.url or "incorrect" in r.text.lower():
        raise RuntimeError("Login failed — wrong admin credentials.")
    print(" done.")


def create_api_token(base_url: str, session: requests.Session) -> str:
    """Mint a permanent admin API token and return its value."""
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


def seed(base_url: str, token: str) -> None:
    """Seed all Cumulonimbus challenges into CTFd."""
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    r = requests.get(f"{base_url}/api/v1/challenges", headers=headers)
    if r.status_code == 403:
        print("ERROR: Token is invalid or CTFd setup was not completed.")
        sys.exit(1)
    r.raise_for_status()

    existing = {c["name"] for c in r.json().get("data", [])}

    print(f"\nSeeding {len(CHALLENGES)} challenges:")
    for challenge in CHALLENGES:
        if challenge["name"] in existing:
            print(f"  [skip]    {challenge['name']}")
            continue
        cid = create_challenge(base_url, headers, challenge)
        create_flag(base_url, headers, cid, challenge["flag"])
        create_tags(base_url, headers, cid, challenge.get("tags", []))
        create_hints(base_url, headers, cid, challenge.get("hints", []))
        print(f"  [created] {challenge['name']}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialise CTFd and seed all Cumulonimbus challenges in one step."
    )
    parser.add_argument("--url", default="http://localhost:8000", help="CTFd base URL")
    parser.add_argument("--ctf-name", default="Cumulonimbus", dest="ctf_name")
    parser.add_argument("--admin-name", default="admin", dest="admin_name")
    parser.add_argument("--admin-email", default="admin@cumulonimbus.local", dest="admin_email")
    parser.add_argument("--admin-password", default="cumulonimbus", dest="admin_password")
    parser.add_argument("--timeout", type=int, default=120, help="Seconds to wait for CTFd to start")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    session = requests.Session()

    print("=== Cumulonimbus CTFd Setup ===\n")

    already_configured = wait_for_ready(base_url, args.timeout)

    if not already_configured:
        run_setup_wizard(
            base_url, session,
            args.ctf_name, args.admin_name, args.admin_email, args.admin_password,
        )
    else:
        print("  CTFd already configured — skipping setup wizard.")
        login(base_url, session, args.admin_name, args.admin_password)

    token = create_api_token(base_url, session)
    seed(base_url, token)

    print(f"\n=== Done! ===")
    print(f"  CTFd URL   : {base_url}")
    print(f"  Admin user : {args.admin_name}")
    print(f"  Admin pass : {args.admin_password}")
    print(f"  API token  : {token}")


if __name__ == "__main__":
    main()
