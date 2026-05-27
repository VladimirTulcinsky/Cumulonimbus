#!/usr/bin/env python3
"""
victim_simulator.py - Automated Victim for Device Code Phishing

Headlessly simulates a victim clicking a device code phishing link and
completing authentication. Requires Playwright:

    pip install playwright
    playwright install chromium

Usage:
  python3 victim_simulator.py \\
      --tenant <tenant_id_or_domain> \\
      --code   <USER_CODE_from_phish.py> \\
      --username <victim@domain> \\
      --password '<password>'
"""

import argparse
import sys
import time

DEVICE_LOGIN_URL = "https://microsoft.com/devicelogin"


def simulate(tenant: str, user_code: str, username: str, password: str):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Playwright not installed. Run:")
        print("      pip install playwright && playwright install chromium")
        sys.exit(1)

    print()
    print("[*] Starting headless browser (Playwright / Chromium)...")
    print(f"[*] Navigating to {DEVICE_LOGIN_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Navigate to device login and submit the user code
        page.goto(DEVICE_LOGIN_URL, wait_until="networkidle")
        page.fill("input[name='otc']", user_code)
        print(f"[*] Submitting user code: {user_code}")
        page.click("input[type='submit']")
        page.wait_for_load_state("networkidle")

        # Step 2: Enter username
        if page.locator("input[type='email']").count() > 0:
            print(f"[*] Entering victim username: {username}")
            page.fill("input[type='email']", username)
            page.click("input[type='submit']")
            page.wait_for_load_state("networkidle")

        # Step 3: Enter password
        if page.locator("input[type='password']").count() > 0:
            print("[*] Entering victim password...")
            page.fill("input[type='password']", password)
            page.click("input[type='submit']")
            page.wait_for_load_state("networkidle")

        # Step 4: Handle "Stay signed in?" prompt if present
        try:
            stay_btn = page.locator("input[type='submit'][value='Yes']")
            if stay_btn.count() > 0:
                stay_btn.click()
                page.wait_for_load_state("networkidle")
        except Exception:
            pass

        # Confirm success — the page should show a completion message
        content = page.content()
        browser.close()

    if any(phrase in content for phrase in ["signed in", "approved", "You have signed", "success"]):
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ✓  VICTIM AUTHENTICATION COMPLETE                          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print("[+] The attacker's phish.py should now receive the access token.")
    else:
        print()
        print("[!] Could not confirm authentication — check credentials or MFA settings.")
        print("    If the tenant has MFA / Conditional Access, disable it first.")
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
