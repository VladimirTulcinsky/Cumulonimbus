import shutil
import traceback

import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
from cumulonimbus.cumulonimbus_parser import CumulonimbusParser
from cumulonimbus.providers.base.authentication_strategy_factory import get_authentication_strategy
from cumulonimbus.providers.base.creation_strategy_factory import get_creation_strategy
from cumulonimbus.providers.base.application_configuration_factory import get_application_configuration


def _report_error(prefix, exc):
    """Print a one-line error, plus a full traceback when verbose mode is on."""
    print(f"{prefix}: {exc}")
    if getattr(global_variables, 'VERBOSE', False):
        traceback.print_exc()
    else:
        print("  Re-run with --verbose (or set CUMULONIMBUS_VERBOSE=1) for the full error.")


def _missing_required_tools(provider, need_cloud_cli=False):
    """Return external tools the requested operation needs but that aren't on
    PATH. Catching these up front avoids a half-deployed lab when, for example,
    a Terraform local-exec calls `az` and it isn't installed."""
    missing = []
    if shutil.which('terraform') is None:
        missing.append('terraform')
    if need_cloud_cli and provider == 'azure' and shutil.which('az') is None:
        missing.append('az (Azure CLI)')
    return missing


def _print_missing_tools(missing):
    print("Missing required tool(s) on PATH: " + ", ".join(missing) + ".")
    print("  These are pre-installed in the Cumulonimbus Docker image — if you see")
    print("  this there, rebuild the image (docker build -t cumulonimbus .) or pull")
    print("  the latest. If you are running locally, install the tool(s) above.")


def run_from_cli():
    import sys

    # Launch the guided interactive shell when invoked with no arguments or the
    # explicit `shell` subcommand. Everything else falls through to the normal
    # flag-based parser so existing scripts keep working unchanged.
    cli_args = sys.argv[1:]
    if not cli_args or cli_args[0] == 'shell':
        from cumulonimbus.shell import run_shell
        cumulonimbus_utils.create_data_directory()
        try:
            return run_shell()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            return 130

    parser = CumulonimbusParser()
    args = parser.parse_args()
    args = args.__dict__

    if args.get('verbose'):
        global_variables.VERBOSE = True

    cumulonimbus_utils.create_data_directory()

    if args.get('command') == 'authenticate':
        raw_name = args.get('name_suffix')
        if raw_name is not None:
            suffix = cumulonimbus_utils.set_name_suffix(raw_name)
            label = cumulonimbus_utils.sanitize_name_label(raw_name)
            if suffix:
                print(f"Session name: {suffix} (your '{label}' plus a random tag so "
                      "it stays unique even if someone else picks the same name).")
            elif raw_name.strip():
                print("Session name had no letters or digits — ignored.")
        try:
            rc = authenticate(provider=args.get('provider'),
                              aws_access_key_id=args.get('aws_access_key_id'),
                              aws_secret_access_key=args.get('aws_secret_access_key'),
                              aws_session_token=args.get('aws_session_token'),
                              service_principal=args.get('service_principal'),
                              client_id=args.get('client_id'), client_secret=args.get('client_secret'),
                              tenant_id=args.get('tenant_id'),
                              subscription_id=args.get('subscription_id'),
                              tenant_domain=args.get('tenant_domain'),
                              region=args.get('region')
                              )
        except (KeyboardInterrupt, SystemExit):
            print('Exiting')
            return 130

        if rc:
            return rc
        print('Authentication successful')
        return 0

    elif args.get('command') == 'create':
        return create(provider=args.get('provider'),
                      app_id=args.get('vulnerable_app_id'))

    elif args.get('command') == 'destroy':
        return destroy(provider=args.get('provider'),
                       app_id=args.get('vulnerable_app_id'))

    elif args.get('command') == 'validate':
        return validate(provider=args.get('provider'),
                        app_id=args.get('vulnerable_app_id'),
                        submitted_flag=args.get('flag'))

    elif args.get('command') == 'hint':
        return hint(provider=args.get('provider'),
                    app_id=args.get('vulnerable_app_id'),
                    level=args.get('hint_level', 1))

    elif args.get('command') == 'list':
        return list_labs(provider=args.get('provider'))


def authenticate(provider,
                 profile=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 service_principal=False,
                 client_id=None, client_secret=None,
                 tenant_id=None,
                 subscription_id=None,
                 tenant_domain=None,
                 region=""):
    print('Authenticating to cloud provider')
    auth_strategy = get_authentication_strategy(provider)

    try:
        credentials = auth_strategy.authenticate(profile=profile,
                                                 aws_access_key_id=aws_access_key_id,
                                                 aws_secret_access_key=aws_secret_access_key,
                                                 aws_session_token=aws_session_token,
                                                 service_principal=service_principal,
                                                 tenant_id=tenant_id,
                                                 client_id=client_id,
                                                 client_secret=client_secret,
                                                 subscription_id=subscription_id,
                                                 tenant_domain=tenant_domain,
                                                 region=region)

        if not credentials:
            print('Authentication failure: no credentials returned')
            return 101

    except Exception as e:
        _report_error('Authentication failure', e)
        return 101

    return 0


def create(provider, app_id):
    try:
        missing = _missing_required_tools(provider, need_cloud_cli=True)
        if missing:
            _print_missing_tools(missing)
            return 101

        auth_strategy = get_authentication_strategy(provider)
        credentials = auth_strategy.get_credentials()

        if not credentials:
            print('No Credentials found. Please authenticate first')
            return 101

        creation_strategy = get_creation_strategy(provider)
        creation_strategy.create(app_id=app_id, credentials=credentials)
        return 0

    except Exception as e:
        _report_error('Creation failure', e)
        return 101


def destroy(provider, app_id):
    try:
        missing = _missing_required_tools(provider)
        if missing:
            _print_missing_tools(missing)
            return 101

        auth_strategy = get_authentication_strategy(provider)
        credentials = auth_strategy.get_credentials()

        if not credentials:
            print('No credentials found. Please authenticate first')
            return 101

        creation_strategy = get_creation_strategy(provider)
        creation_strategy.destroy(app_id=app_id, credentials=credentials)
        return 0

    except Exception as e:
        _report_error('Destruction failure', e)
        return 101


def hint(provider, app_id, level):
    try:
        app_config = get_application_configuration(provider, app_id)
        hints = app_config.get_hints()
        difficulty = app_config.get_difficulty()

        if not hints:
            print(f"No hints are configured for {app_id}.")
            return 1

        max_level = max(hints.keys())
        level = min(level, max_level)

        print(f"[{app_id}]  Difficulty: {difficulty}")
        print(f"Hint (level {level}/{max_level}): {hints[level]}")
        if level < max_level:
            print(f"  Run with --level {level + 1} for a stronger hint.")
        return 0

    except Exception as e:
        _report_error('Hint failure', e)
        return 101


def list_labs(provider):
    if provider == 'aws':
        labs = sorted(global_variables.AWS_APP_LIST)
    else:
        labs = sorted(global_variables.AZURE_APP_LIST)
    print(f"Available {provider.upper()} labs ({len(labs)}):")
    for lab in labs:
        print(f"  {lab}")
    return 0


def validate(provider, app_id, submitted_flag):
    try:
        app_config = get_application_configuration(provider, app_id)
        correct_flag = app_config.get_flag()

        if correct_flag is None:
            print(f"Flag validation is not configured for {app_id}.")
            return 1

        if submitted_flag.strip() == correct_flag.strip():
            print(f"Correct! Well done — you have successfully completed {app_id}.")
            return 0
        else:
            print("Incorrect flag. Keep trying!")
            return 1

    except Exception as e:
        _report_error('Validation failure', e)
        return 101
