import cumulonimbus.global_variables as global_variables
import cumulonimbus.core.utils as cumulonimbus_utils
from cumulonimbus.cumulonimbus_parser import CumulonimbusParser
from cumulonimbus.providers.base.authentication_strategy_factory import get_authentication_strategy
from cumulonimbus.providers.base.creation_strategy_factory import get_creation_strategy
from cumulonimbus.providers.base.application_configuration_factory import get_application_configuration


def run_from_cli():
    parser = CumulonimbusParser()
    args = parser.parse_args()
    args = args.__dict__

    cumulonimbus_utils.create_data_directory()

    if args.get('command') == 'authenticate':
        try:
            authenticate(provider=args.get('provider'),
                         aws_access_key_id=args.get('aws_access_key_id'),
                         aws_secret_access_key=args.get('aws_secret_access_key'),
                         aws_session_token=args.get('aws_session_token'),
                         service_principal=args.get('service_principal'),
                         client_id=args.get('client_id'), client_secret=args.get('client_secret'),
                         tenant_id=args.get('tenant_id'),
                         subscription_id=args.get('subscription_id'),
                         region=args.get('region')
                         )
            print('Authentication successful')

        except (KeyboardInterrupt, SystemExit):
            print('Exiting')
            return 130

    elif args.get('command') == 'create':
        create(provider=args.get('provider'),
               app_id=args.get('vulnerable_app_id'))

    elif args.get('command') == 'destroy':
        destroy(provider=args.get('provider'),
                app_id=args.get('vulnerable_app_id'))

    elif args.get('command') == 'validate':
        return validate(provider=args.get('provider'),
                        app_id=args.get('vulnerable_app_id'),
                        submitted_flag=args.get('flag'))


def authenticate(provider,
                 profile=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 service_principal=False,
                 client_id=None, client_secret=None,
                 tenant_id=None,
                 subscription_id=None,
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
                                                 subscription_id=subscription_id)

        if not credentials:
            return 101

    except Exception as e:
        print(f'Authentication failure: {e}')
        return 101


def create(provider, app_id):
    try:
        auth_strategy = get_authentication_strategy(provider)
        credentials = auth_strategy.get_credentials()

        if not credentials:
            print('No Credentials found. Please authenticate first')
            return 101

        creation_strategy = get_creation_strategy(provider)
        creation_strategy.create(app_id=app_id, credentials=credentials)

    except Exception as e:
        print(f'Creation failure: {e}')
        return 101


def destroy(provider, app_id):
    try:
        auth_strategy = get_authentication_strategy(provider)
        credentials = auth_strategy.get_credentials()

        if not credentials:
            return 101

        creation_strategy = get_creation_strategy(provider)
        creation_strategy.destroy(app_id=app_id, credentials=credentials)

    except Exception as e:
        print(f'Destruction failure: {e}')
        return 101


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
        print(f'Validation failure: {e}')
        return 101
