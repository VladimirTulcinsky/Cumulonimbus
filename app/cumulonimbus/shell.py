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
import ipaddress
import os
import shutil
import subprocess
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
    print(f"  Category: {info['category']}")
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
    print(f"\n{len(labs)} Azure labs available. Pick one to read a short, "
          "spoiler-free summary and its objective.")
    while True:
        choice = _choose("Azure labs", labs, allow_back=True)
        if choice is None:
            return
        _show_lab_info(choice)


def _ctfd_dir():
    return os.path.abspath(os.path.join(global_variables.ROOT_DIR, "..", "..", "ctfd"))


def _ensure_ctfd_ssh_key():
    """Return (public_key, error). Generates an RSA keypair under .data/.ssh
    for the CTFd VM admin if one doesn't exist yet. Azure's admin_ssh_key only
    accepts RSA keys, so any older non-RSA key is regenerated."""
    ssh_dir = os.path.join(global_variables.ROOT_DIR, ".data", ".ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    key_path = os.path.join(ssh_dir, "ctfd_admin")
    pub_path = key_path + ".pub"

    if os.path.exists(pub_path):
        try:
            existing = open(pub_path).read().strip()
        except OSError:
            existing = ""
        if existing.startswith("ssh-rsa"):
            return existing, None
        # Wrong key type (e.g. an ed25519 key from an earlier version) — Azure
        # rejects it, so remove it and regenerate as RSA.
        for path in (key_path, pub_path):
            try:
                os.remove(path)
            except OSError:
                pass

    try:
        result = subprocess.run(
            ["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-C", "ctfd-admin", "-f", key_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
    except FileNotFoundError:
        return None, "ssh-keygen not found"
    if result.returncode != 0:
        return None, (result.stderr or "ssh-keygen failed").strip()
    with open(pub_path) as f:
        return f.read().strip(), None


def _do_ctfd(provider):
    """Deploy the persistent, shared CTFd scoreboard on Azure — a singleton VM
    created by the ctfd/azure Terraform that stays up independently of this
    container. (There is no local docker-compose option anymore.)"""
    print()
    if not os.environ.get("AZURE_CLIENT_ID"):
        print("  Authenticate to Azure first (the Authenticate menu option).")
        return

    ctfd_azure = os.path.join(_ctfd_dir(), "azure")
    if not os.path.isdir(ctfd_azure) or shutil.which("terraform") is None:
        print("  Can't deploy from here — this needs the ctfd/azure Terraform files")
        print("  and the terraform CLI. From a host checkout of the repo:")
        print("    cd ctfd/azure && terraform init && terraform apply \\")
        print('      -var "admin_ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"')
        return

    cidr = _select_ctfd_cidr()
    if cidr is None:
        return

    admin_pw = _prompt("CTFd admin password", default="cumulonimbus")
    vm_size = _prompt("VM size (hit Enter for default; change if you hit SkuNotAvailable)",
                      default="Standard_D2s_v3")
    pub_key, err = _ensure_ctfd_ssh_key()
    if not pub_key:
        print(f"  Could not prepare an SSH key for the VM: {err}")
        return

    print("\n  This deploys a PERSISTENT CTFd scoreboard VM in Azure (real")
    print("  infrastructure — it incurs cost until destroyed). It is a singleton:")
    print("  only one can exist, and it stays up independently of this container.")
    if not _confirm("Deploy now?", default=True):
        print("  Cancelled.")
        return

    env = os.environ.copy()
    env["ARM_CLIENT_ID"] = os.environ["AZURE_CLIENT_ID"]
    env["ARM_CLIENT_SECRET"] = os.environ["AZURE_CLIENT_SECRET"]
    env["ARM_TENANT_ID"] = os.environ["AZURE_TENANT_ID"]
    env["ARM_SUBSCRIPTION_ID"] = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    # Config/secrets via TF_VAR_* env keeps them off the command line.
    env["TF_VAR_player_allowed_cidr"] = cidr
    env["TF_VAR_ssh_allowed_cidr"] = cidr
    env["TF_VAR_admin_ssh_public_key"] = pub_key
    env["TF_VAR_ctfd_admin_password"] = admin_pw
    env["TF_VAR_vm_size"] = vm_size
    env["TF_VAR_location"] = os.environ.get("AZURE_LOCATION", "West Europe")

    chdir = f"-chdir={ctfd_azure}"
    if subprocess.run(["terraform", chdir, "init", "-input=false"], env=env).returncode != 0:
        print("  terraform init failed (see output above).")
        return
    if subprocess.run(["terraform", chdir, "apply", "-auto-approve", "-input=false"], env=env).returncode != 0:
        print("  Deploy failed (see Terraform output above).")
        print("  - SkuNotAvailable? Re-run and pick a different VM size (e.g.")
        print("    Standard_B2ms, Standard_D2as_v5), or authenticate to another region.")
        print("  - 'already exists'? That's the singleton — there can be only one.")
        return

    out = subprocess.run(["terraform", chdir, "output", "-raw", "ctfd_url"],
                         env=env, capture_output=True, text=True)
    url = out.stdout.strip() if out.returncode == 0 else "http://<vm-ip>:8001"
    ip = subprocess.run(["terraform", chdir, "output", "-raw", "public_ip"],
                        env=env, capture_output=True, text=True)
    vm_ip = ip.stdout.strip() if ip.returncode == 0 else "<vm-ip>"
    key_path = os.path.join(global_variables.ROOT_DIR, ".data", ".ssh", "ctfd_admin")
    print(f"\n  CTFd scoreboard deploying at: {url}")
    print("  First boot installs Docker and seeds the challenges — give it a few")
    print("  minutes before the URL responds. Admin login: admin / the password you set.")
    print("\n  SSH to the VM (use -i with the key this deploy generated):")
    print(f"    ssh -i {key_path} ctfdadmin@{vm_ip}")
    print("  Note: Terraform state and that SSH key live in this container; for")
    print("  durable management run the ctfd/azure Terraform from a host. The VM persists.")



# Names of the singleton CTFd-on-Azure resources (see ctfd/azure/).
_CTFD_RG = "cumulonimbus-ctfd"
_CTFD_NSG = "ctfd-nsg"
_CTFD_RULE = "CTFd-Azure"


def _valid_cidr(value):
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False


def _select_ctfd_cidr():
    """Interactively choose an allowed source CIDR for the scoreboard. Suggests
    the current public IP first. Returns the CIDR string, or None if cancelled."""
    my_ip = global_variables.ATTACKER_PUBLIC_IP.get("azure", "0.0.0.0")
    suggested = f"{my_ip}/32" if my_ip and my_ip != "0.0.0.0" else None

    print("\n  Who should be able to reach the CTFd scoreboard (port 8001)?")
    options = []
    if suggested:
        options.append(f"Restrict to my IP only ({suggested})")
    options.append("Enter a custom CIDR")
    options.append("Open to the public internet (0.0.0.0/0)")

    choice = _choose("Allowed source", options, allow_back=True)
    if choice is None:
        return None
    if choice.startswith("Restrict to my IP"):
        return suggested
    if choice.startswith("Enter a custom"):
        cidr = _prompt("CIDR (e.g. 203.0.113.5/32 or 203.0.113.0/24)")
        if not _valid_cidr(cidr):
            print("  That doesn't look like a valid IP or CIDR.")
            return None
        return cidr
    if not _confirm("Open the scoreboard to the ENTIRE internet?", default=False):
        print("  Cancelled.")
        return None
    return "0.0.0.0/0"


def _do_ctfd_cidr(provider):
    """Change which source IP/CIDR may reach the already-deployed Azure CTFd
    scoreboard (updates the singleton's NSG rule live, via az)."""
    if not os.environ.get("AZURE_CLIENT_ID"):
        print("\n  Authenticate to Azure first (the Authenticate menu option).")
        return
    cidr = _select_ctfd_cidr()
    if cidr is None:
        return
    print(f"\n  This sets the scoreboard's allowed source to: {cidr}")
    if not _confirm("Apply to the running instance now?", default=True):
        print("  Cancelled.")
        return
    _apply_ctfd_nsg_cidr(cidr)


def _apply_ctfd_nsg_cidr(cidr):
    # Use an isolated az session dir so this admin action doesn't disturb any
    # `az login` you're using for a lab.
    env = os.environ.copy()
    env["AZURE_CONFIG_DIR"] = os.path.join(global_variables.ROOT_DIR, ".data", ".azure-ctfd-admin")
    try:
        login = subprocess.run(
            ["az", "login", "--service-principal",
             "-u", os.environ["AZURE_CLIENT_ID"],
             "-p", os.environ["AZURE_CLIENT_SECRET"],
             "--tenant", os.environ["AZURE_TENANT_ID"]],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
        if login.returncode != 0:
            print("  az login failed: " + (login.stderr or "").strip())
            return
        subscription = os.environ.get("AZURE_SUBSCRIPTION_ID")
        if subscription:
            subprocess.run(["az", "account", "set", "--subscription", subscription],
                           env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        update = subprocess.run(
            ["az", "network", "nsg", "rule", "update",
             "--resource-group", _CTFD_RG, "--nsg-name", _CTFD_NSG, "--name", _CTFD_RULE,
             "--source-address-prefixes", cidr],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        )
        if update.returncode != 0:
            print("  Could not update the rule: " + (update.stderr or "").strip())
            print("  Has the CTFd scoreboard been deployed? See ctfd/azure/README.md.")
            return
        print(f"  Done — the scoreboard now accepts traffic from {cidr}.")
        print(f'  To persist this, set player_allowed_cidr="{cidr}" in ctfd/azure and')
        print("  re-apply Terraform (otherwise a future terraform apply resets it).")
    except FileNotFoundError:
        print("  The Azure CLI (az) was not found.")
    finally:
        try:
            subprocess.run(["az", "logout"], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


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
    ("Start the CTFd scoreboard (Azure)", _do_ctfd),
    ("Set CTFd scoreboard access (CIDR)", _do_ctfd_cidr),
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

