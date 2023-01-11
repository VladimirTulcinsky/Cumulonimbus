import cumulonimbus.global_variables as global_variables
from cumulonimbus.cumulonimbus_parser import CumulonimbusParser
from cumulonimbus.providers.base.authentication_strategy_factory import get_authentication_strategy


def run_from_cli():
    parser = CumulonimbusParser()
    args = parser.parse_args()
    args = args.__dict__

    if args.get('command') == 'authenticate':
        try:
            authenticate(provider=args.get('provider'),
                         # AWS
                         aws_access_key_id=args.get('aws_access_key_id'),
                         aws_secret_access_key=args.get(
                             'aws_secret_access_key'),
                         aws_session_token=args.get('aws_session_token'),
                         # Azure
                         user_account=args.get('user_account'),
                         service_principal=args.get('service_principal'),
                         client_id=args.get('client_id'), client_secret=args.get('client_secret'),
                         username=args.get('username'), password=args.get('password'),
                         tenant_id=args.get('tenant_id'),
                         subscription_id=args.get('subscription_id'),

                         # General
                         region=args.get('region')
                         )
            print('Authentication successful')

        except (KeyboardInterrupt, SystemExit):
            print('Exiting')
            return 130

    elif args.get('command') == 'create':
        print('Creating vulnerable application')
        pass


def authenticate(provider,
                 # AWS
                 profile=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 # Azure
                 user_account=False,
                 service_principal=False,
                 client_id=None, client_secret=None,
                 username=None, password=None,
                 tenant_id=None,
                 subscription_id=None,

                 # General
                 region="",
                 programmatic_execution=True):
    """
    Run Cumulonimbus.
    """

    print('Authenticating to cloud provider')
    auth_strategy = get_authentication_strategy(provider)

    try:
        credentials = auth_strategy.authenticate(profile=profile,
                                                 aws_access_key_id=aws_access_key_id,
                                                 aws_secret_access_key=aws_secret_access_key,
                                                 aws_session_token=aws_session_token,
                                                 user_account=user_account,
                                                 service_principal=service_principal,
                                                 tenant_id=tenant_id,
                                                 client_id=client_id,
                                                 client_secret=client_secret,
                                                 username=username,
                                                 password=password)

        if not credentials:
            return 101
    except Exception as e:
        print(f'Authentication failure: {e}')
        return 101
