#!/usr/bin/env python3
"""Interactive, guided shell for Cumulonimbus.

This wraps the same actions as the flag-based CLI (authenticate / create /
destroy / validate / hint / list) but walks the user through them with
prompts, so newcomers don't have to memorise the command syntax. It also
captures an optional per-player "session name" used to namespace deployed
resources, which lets a whole class share a single set of cloud credentials in
one tenant/account without their resources colliding.
"""

import getpass
import textwrap

import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
from cumulonimbus.cumulonimbus_parser import AWS_REGIONS, AZURE_REGIONS
from cumulonimbus.lab_info import AZURE_LAB_INFO


def _print_banner():
    print()
    print("=" * 60)
    print(f"  {global_variables.APP_NAME} — interactive shell")
    print("=" * 60)
    suffix = cumulonimbus_utils.get_name_suffix()
    if suffix:
        print(f"  Session name: {suffix}  (resources are namespaced with this)")
    else:
        print("  Tip: running a CTF for a class? Share ONE set of credentials and")
        print("  give each person a session name (set during Authenticate) so you")
        print("  can all play in the same tenant/account without collisions.")
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


def _choose_app(provider, action_label):
    if provider == "aws":
        labs = sorted(global_variables.AWS_APP_LIST)
    else:
        labs = sorted(global_variables.AZURE_APP_LIST)
    return _choose(f"Which lab do you want to {action_label}?", labs, allow_back=True)


PROVIDER_LABELS = {"azure": "Azure", "aws": "AWS"}


def _choose_play():
    """Top-level 'what do you want to play?' menu.

    Returns 'azure', 'aws', or None when the user chooses to quit.
    """
    options = ["Azure", "AWS (work in progress)", "Quit"]
    choice = _choose("What do you want to play?", options)
    if choice == "Azure":
        return "azure"
    if choice.startswith("AWS"):
        return "aws"
    return None


def _setup_session_name():
    """Prompt for and persist the per-player session name."""
    print()
    print("A 'session name' namespaces the resources you deploy (e.g. resource")
    print("groups, IAM users). If several people share ONE set of cloud")
    print("credentials in the same tenant/account — for example a class doing a")
    print("CTF together — each person should pick a unique name (their initials,")
    print("a team name, etc.) so nobody's lab collides with anybody else's.")
    print("Leave it blank if you are the only one using these credentials.")
    print(f"(Letters and digits only, up to {cumulonimbus_utils.NAME_SUFFIX_LABEL_MAX} "
          "characters — e.g. 'vt', 'team3', 'aliceb'. A short random tag is")
    print("added automatically, so two people who pick the same name still get")
    print("unique resources.)")
    current = cumulonimbus_utils.get_name_suffix()
    raw = _prompt_optional(
        f"Session name{f' [{current}]' if current else ''}"
    )
    if not raw and current:
        return current
    suffix = cumulonimbus_utils.set_name_suffix(raw)
    label = cumulonimbus_utils.sanitize_name_label(raw)
    if suffix:
        print(f"  Session name: {suffix}  (your '{label}' plus a random tag for uniqueness)")
        if label != raw.strip().lower():
            print(f"    (your input was shortened/cleaned to '{label}'.)")
    elif raw.strip():
        print("  That name has no letters or digits, so no session name was set "
              "(resources use only their random suffix).")
    else:
        print("  No session name set (resources use only their random suffix).")
    return suffix


def _do_authenticate(provider):
    from cumulonimbus.__main__ import authenticate

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
        print("\nAuthentication successful. You can now start a lab.")


def _do_create(provider):
    from cumulonimbus.__main__ import create

    app_id = _choose_app(provider, "start")
    if not app_id:
        return
    suffix = cumulonimbus_utils.get_name_suffix()
    namespacing = f" (namespaced as '{suffix}')" if suffix else ""
    print(f"\nStarting '{app_id}'{namespacing}. This provisions real cloud "
          "infrastructure and may incur charges.")
    if not _confirm("Continue?", default=True):
        print("Cancelled.")
        return
    create(provider=provider, app_id=app_id)


def _do_destroy(provider):
    from cumulonimbus.__main__ import destroy

    app_id = _choose_app(provider, "destroy")
    if not app_id:
        return
    if not _confirm(f"Destroy '{app_id}'? This removes its cloud resources", default=True):
        print("Cancelled.")
        return
    destroy(provider=provider, app_id=app_id)


def _do_validate(provider):
    from cumulonimbus.__main__ import validate

    app_id = _choose_app(provider, "submit a flag for")
    if not app_id:
        return
    flag = _prompt("Enter the flag you captured")
    validate(provider=provider, app_id=app_id, submitted_flag=flag)


def _do_hint(provider):
    from cumulonimbus.__main__ import hint

    app_id = _choose_app(provider, "get a hint for")
    if not app_id:
        return
    level = _choose(
        "How strong a hint?",
        ["1 - gentle nudge", "2 - moderate", "3 - explicit"],
    )
    hint(provider=provider, app_id=app_id, level=int(level[0]))


def _show_lab_info(app_id):
    info = AZURE_LAB_INFO.get(app_id)
    print()
    if not info:
        print(f"  No description is available for '{app_id}' yet.")
        return
    wrap = textwrap.TextWrapper(width=74, initial_indent="    ",
                                subsequent_indent="    ")
    print(f"  {info['name']}  [{app_id}]")
    print(f"  Difficulty: {info['difficulty']}   |   Category: {info['category']}")
    print("\n  What it is:")
    print(wrap.fill(info['summary']))
    print("\n  Objective:")
    print(wrap.fill(info['objective']))
    print(f"\n  Start it from the menu, or: cnimbus azure create --app-id {app_id}")


def _do_list(provider):
    from cumulonimbus.__main__ import list_labs

    if provider != "azure":
        # Other providers don't have the descriptive catalog yet.
        list_labs(provider=provider)
        return

    labs = sorted(global_variables.AZURE_APP_LIST)
    labels = [
        f"{lab}  —  {AZURE_LAB_INFO.get(lab, {}).get('difficulty', '?')}"
        for lab in labs
    ]
    label_to_app = dict(zip(labels, labs))
    print(f"\n{len(labs)} Azure labs available. Pick one to read a short, "
          "spoiler-free summary and its objective.")
    while True:
        choice = _choose("Azure labs", labels, allow_back=True)
        if choice is None:
            return
        _show_lab_info(label_to_app[choice])


def _print_aws_wip():
    print()
    print("  " + "-" * 56)
    print("  🚧  AWS labs are a WORK IN PROGRESS on this build.")
    print("  This release focuses on Azure. AWS labs are being developed")
    print("  on a separate branch and are not playable here yet.")
    print("  " + "-" * 56)


def _do_session_name(provider):
    _setup_session_name()


# Provider-scoped actions, shown after a provider is chosen.
_ACTIONS = [
    ("Authenticate", _do_authenticate),
    ("Start a lab", _do_create),
    ("Get a hint", _do_hint),
    ("Submit a flag", _do_validate),
    ("Browse labs / get lab info", _do_list),
    ("Destroy a lab", _do_destroy),
    ("Set / change my session name", _do_session_name),
]

_BACK_LABEL = "Back (choose a different provider)"
_QUIT_LABEL = "Quit"


def _provider_menu(provider):
    """Loop the action menu for a chosen provider.

    Returns 'quit' to exit the shell entirely, or 'back' to return to the
    provider selection.
    """
    while True:
        labels = [label for label, _ in _ACTIONS] + [_BACK_LABEL, _QUIT_LABEL]
        choice = _choose(
            f"{PROVIDER_LABELS[provider]} — what do you want to do?", labels
        )
        if choice == _QUIT_LABEL:
            return "quit"
        if choice == _BACK_LABEL:
            return "back"
        action = dict(_ACTIONS)[choice]
        try:
            action(provider)
        except KeyboardInterrupt:
            print("\n(cancelled — back to menu)")
        print()


def run_shell():
    _print_banner()
    while True:
        provider = _choose_play()
        if provider is None:
            print("Goodbye.")
            return 0
        if provider == "aws":
            # AWS is a work in progress on this Azure-focused branch.
            _print_aws_wip()
            continue
        if _provider_menu(provider) == "quit":
            print("Goodbye.")
            return 0

