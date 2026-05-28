#!/usr/bin/env python3
"""
victim_simulator.py - Automated Victim for Device Code Phishing

Headlessly simulates a victim clicking a device code phishing link and
completing authentication using a pre-installed Playwright / Chromium.

Usage:
  python3 victim_simulator.py \\
      --tenant   <tenant_id_or_domain> \\
      --code     <USER_CODE_from_phish.py> \\
      --username <victim@domain> \\
      --password '<password>'
"""

import argparse
import sys
import time
from playwright.sync_api import sync_playwright

DEVICE_LOGIN_URL = "https://microsoft.com/devicelogin"

SUCCESS_PHRASES = [
    "You have signed in",
    "You're signed in",
    "signed in to",
    "You have approved",
    "authentication complete",
]


def simulate(tenant: str, user_code: str, username: str, password: str):
    print()
    print("[*] Starting headless browser (Playwright / Chromium)...")
    print(f"[*] Navigating to {DEVICE_LOGIN_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context().new_page()
        page.set_default_timeout(30000)

        page.goto(DEVICE_LOGIN_URL, wait_until="domcontentloaded")

        # Step 1: submit the user code
        page.wait_for_selector("input[name='otc']", timeout=15000)
        page.fill("input[name='otc']", user_code)
        print(f"[*] Submitting user code: {user_code}")
        page.locator("input[type='submit']").click()

        # Drive through the remaining Microsoft login pages in a loop.
        # After credentials, Microsoft shows an app-confirmation page
        # ("Are you trying to sign in to Microsoft Office?") that must be
        # clicked through before a token is issued. The loop handles that
        # page and any other prompts (KMSI, etc.) generically.
        deadline = time.time() + 90
        while time.time() < deadline:
            try:
                page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass

            content = page.content()

            if any(phrase in content for phrase in SUCCESS_PHRASES):
                break

            if page.locator("input[type='email']").count() > 0:
                print(f"[*] Entering username: {username}")
                page.fill("input[type='email']", username)
                page.locator("input[type='submit']").click()
                continue

            if page.locator("input[type='password']").count() > 0:
                print("[*] Entering password...")
                page.fill("input[type='password']", password)
                page.locator("input[type='submit']").click()
                continue

            # App confirmation, KMSI, or any other submit-driven prompt
            submit = page.locator("input[type='submit']")
            if submit.count() > 0:
                print("[*] Advancing through prompt...")
                submit.first.click()
                continue

            time.sleep(1)

        content = page.content()
        browser.close()

    if any(phrase in content for phrase in SUCCESS_PHRASES):
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ✓  VICTIM AUTHENTICATION COMPLETE                          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print("[+] The attacker's phish.py should now receive the access token.")
    else:
        print()
        print("[!] Could not confirm authentication — timed out or unexpected page.")
        print("    Check that credentials are correct and MFA / Conditional Access")
        print("    is not blocking the sign-in.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Device Code Phishing — Victim Simulator")
    parser.add_argument("--tenant",   required=True, help="Azure AD tenant ID or primary domain")
    parser.add_argument("--code",     required=True, help="User code displayed by phish.py")
    parser.add_argument("--username", required=True, help="Victim's UPN (email)")
    parser.add_argument("--password", required=True, help="Victim's password")
    args = parser.parse_args()

    simulate(args.tenant, args.code, args.username, args.password)


if __name__ == "__main__":
    main()
