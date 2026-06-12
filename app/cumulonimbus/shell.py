#!/usr/bin/env python3
"""Interactive, guided shell for Cumulonimbus.

This wraps the same actions as the flag-based CLI (authenticate / create /
destroy / validate / hint / ttl / list) but walks the user through them with
prompts, so newcomers don't have to memorise the command syntax. It also
captures an optional per-player "session name" used to namespace deployed
resources, which lets a whole class share a single set of cloud credentials in
one tenant/account without their resources colliding.
"""

import getpass

import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
from cumulonimbus.cumulonimbus_parser import AWS_REGIONS, AZURE_REGIONS


def _print_banner():
    print()
    print("=" * 60)
    print(f"  {global_variables.APP_NAME} — interactive shell")
    print("=" * 60)
    suffix = cumulonimbus_utils.get_name_suffix()
    if suffix:
        print(f"  Session name: {suffix}  (resources are namespaced with this)")
    print("  Type the number of an option and press Enter. Ctrl-C to quit.")
    print()


def _prompt(message, default=None):
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            answer = input(f"{message}{suffix}: ").strip()
        except EOFError:
            raise KeyboardInterrupt
        if answer:
            return answer
        if default is not None:
            return default
        print("  This value is required.")


def _prompt_optional(message):
    try:
        return input(f"{message}: ").strip()
    except EOFError:
        raise KeyboardInterrupt


def _prompt_secret(message):
    while True:
        value = getpass.getpass(f"{message}: ").strip()
        if value:
            return value
        print("  This value is required.")


def _choose(message, options, allow_back=False):
    """Render a numbered menu and return the chosen option (a string).

    Returns None if allow_back is set and the user picks the back/cancel entry.
    """
    print(f"\n{message}")
    for index, option in enumerate(options, start=1):
        print(f"  {index}) {option}")
    back_index = len(options) + 1
    if allow_back:
        print(f"  {back_index}) Back")
    while True:
        raw = _prompt("Choice")
        if not raw.isdigit():
            print("  Enter the number of an option.")
            continue
        choice = int(raw)
        if 1 <= choice <= len(options):
            return options[choice - 1]
        if allow_back and choice == back_index:
            return None
        print("  That option does not exist.")


def _confirm(message, default=True):
    hint = "Y/n" if default else "y/N"
    answer = _prompt_optional(f"{message} ({hint})").lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def _choose_provider(allow_back=False):
    provider = _choose("Which cloud provider?", ["aws", "azure"], allow_back=allow_back)
    return provider


def _choose_app(provider, action_label):
    if provider == "aws":
        labs = sorted(global_variables.AWS_APP_LIST)
    else:
        labs = sorted(global_variables.AZURE_APP_LIST)
    return _choose(f"Which lab do you want to {action_label}?", labs, allow_back=True)


def _setup_session_name():
    """Prompt for and persist the per-player session name."""
    print()
    print("A 'session name' namespaces the resources you deploy (e.g. resource")
    print("groups, IAM users). If several people share ONE set of cloud")
    print("credentials in the same tenant/account — for example a class doing a")
    print("CTF together — each person should pick a unique name (their initials,")
    print("a team name, etc.) so nobody's lab collides with anybody else's.")
    print("Leave it blank if you are the only one using these credentials.")
    current = cumulonimbus_utils.get_name_suffix()
    raw = _prompt_optional(
        f"Session name (letters/digits){f' [{current}]' if current else ''}"
    )
    if not raw and current:
        return current
    suffix = cumulonimbus_utils.set_name_suffix(raw)
    if suffix:
        print(f"  Session name set to: {suffix}")
    else:
        print("  No session name set (resources use only their random suffix).")
    return suffix


def _do_authenticate():
    from cumulonimbus.__main__ import authenticate

    provider = _choose_provider(allow_back=True)
    if provider is None:
        return

    _setup_session_name()

    if provider == "aws":
        access_key_id = _prompt("AWS Access Key ID")
        secret_access_key = _prompt_secret("AWS Secret Access Key")
        session_token = _prompt_optional("AWS Session Token (optional, press Enter to skip)")
        region = _choose("AWS region to deploy to", AWS_REGIONS)
        result = authenticate(
            provider="aws",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token or None,
            region=region,
        )
    else:
        client_id = _prompt("Azure Client ID (app id)")
        client_secret = _prompt_secret("Azure Client Secret")
        tenant_id = _prompt("Azure Tenant ID")
        subscription_id = _prompt("Azure Subscription ID")
        tenant_domain = _prompt("Azure Tenant domain (e.g. contoso.onmicrosoft.com)")
        region = _choose("Azure region to deploy to", AZURE_REGIONS)
        result = authenticate(
            provider="azure",
            service_principal=True,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            tenant_domain=tenant_domain,
            region=region,
        )

    if result:
        print("\nAuthentication failed. Please check your credentials and try again.")
    else:
        print("\nAuthentication successful. You can now deploy a lab.")


def _require_provider_for(action_label):
    provider = _choose_provider(allow_back=True)
    if provider is None:
        return None, None
    app_id = _choose_app(provider, action_label)
    return provider, app_id


def _do_create():
    from cumulonimbus.__main__ import create

    provider, app_id = _require_provider_for("deploy")
    if not app_id:
        return
    suffix = cumulonimbus_utils.get_name_suffix()
    namespacing = f" (namespaced as '{suffix}')" if suffix else ""
    print(f"\nDeploying '{app_id}'{namespacing}. This provisions real cloud "
          "infrastructure and may incur charges.")
    if not _confirm("Continue?", default=True):
        print("Cancelled.")
        return
    create(provider=provider, app_id=app_id)


def _do_destroy():
    from cumulonimbus.__main__ import destroy

    provider, app_id = _require_provider_for("destroy")
    if not app_id:
        return
    if not _confirm(f"Destroy '{app_id}'? This removes its cloud resources", default=True):
        print("Cancelled.")
        return
    destroy(provider=provider, app_id=app_id)


def _do_validate():
    from cumulonimbus.__main__ import validate

    provider, app_id = _require_provider_for("validate")
    if not app_id:
        return
    flag = _prompt("Enter the flag you captured")
    validate(provider=provider, app_id=app_id, submitted_flag=flag)


def _do_hint():
    from cumulonimbus.__main__ import hint

    provider, app_id = _require_provider_for("get a hint for")
    if not app_id:
        return
    level = _choose(
        "How strong a hint?",
        ["1 - gentle nudge", "2 - moderate", "3 - explicit"],
    )
    hint(provider=provider, app_id=app_id, level=int(level[0]))


def _do_ttl():
    from cumulonimbus.__main__ import ttl

    provider, app_id = _require_provider_for("auto-destroy")
    if not app_id:
        return
    while True:
        raw = _prompt("Auto-destroy after how many hours?")
        try:
            hours = float(raw)
            if hours > 0:
                break
        except ValueError:
            pass
        print("  Enter a positive number, e.g. 4 or 1.5")
    ttl(provider=provider, app_id=app_id, hours=hours)


def _do_list():
    from cumulonimbus.__main__ import list_labs

    provider = _choose_provider(allow_back=True)
    if provider is None:
        return
    list_labs(provider=provider)


_MENU = [
    ("Authenticate to a cloud provider", _do_authenticate),
    ("List available labs", _do_list),
    ("Deploy (create) a lab", _do_create),
    ("Get a hint for a lab", _do_hint),
    ("Submit / validate a flag", _do_validate),
    ("Schedule auto-destroy (TTL)", _do_ttl),
    ("Destroy a lab", _do_destroy),
    ("Set / change my session name", lambda: _setup_session_name()),
    ("Quit", None),
]


def run_shell():
    _print_banner()
    while True:
        labels = [label for label, _ in _MENU]
        choice = _choose("What would you like to do?", labels)
        action = dict(_MENU)[choice]
        if action is None:
            print("Goodbye.")
            return 0
        try:
            action()
        except KeyboardInterrupt:
            print("\n(cancelled — back to menu)")
        print()
