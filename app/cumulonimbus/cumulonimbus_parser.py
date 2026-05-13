#!/usr/bin/env python3
import argparse
import cumulonimbus.global_variables as global_variables


class CumulonimbusParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            epilog='To get additional help on a specific provider run: {}.py <provider> -h'.format(global_variables.APP_NAME))

        self.common_providers_args_parser = argparse.ArgumentParser(
            add_help=False)

        self.subparsers = self.parser.add_subparsers(title="The provider you want to run {} against".format(global_variables.APP_NAME),
                                                     dest="provider")

        self._init_aws_parser()
        self._init_azure_parser()

    def _init_aws_parser(self):
        aws_parser = self.subparsers.add_parser("aws",
                                                parents=[
                                                    self.common_providers_args_parser],
                                                help="Run {} against an Amazon Web Services account".format(global_variables.APP_NAME))

        aws_cmd_parser = aws_parser.add_subparsers(title="The command you want to run",
                                                   dest="command")

        aws_cmd_auth_parser = aws_cmd_parser.add_parser(
            "authenticate", help="Authenticate {} against an Amazon Web Services account".format(global_variables.APP_NAME))
        aws_cmd_create_parser = aws_cmd_parser.add_parser(
            "create", help="Create a vulnerable application in an Amazon Web Services account")
        aws_cmd_destroy_parser = aws_cmd_parser.add_parser(
            "destroy", help="Destroy a vulnerable application in an Amazon Web Services account")
        aws_cmd_validate_parser = aws_cmd_parser.add_parser(
            "validate", help="Validate a captured flag for an Amazon Web Services application")
        aws_cmd_hint_parser = aws_cmd_parser.add_parser(
            "hint", help="Get a hint for an Amazon Web Services application")
        aws_cmd_ttl_parser = aws_cmd_parser.add_parser(
            "ttl", help="Schedule auto-destroy for an Amazon Web Services application")

        # Authentication parameters
        aws_auth_params = aws_cmd_auth_parser.add_argument_group(
            'Authentication parameters')

        aws_auth_params.add_argument('--access-key-id',
                                     action='store',
                                     default=None,
                                     dest='aws_access_key_id',
                                     help='AWS Access Key ID')
        aws_auth_params.add_argument('--secret-access-key',
                                     action='store',
                                     default=None,
                                     dest='aws_secret_access_key',
                                     help='AWS Secret Access Key')
        aws_auth_params.add_argument('--session-token',
                                     action='store',
                                     default=None,
                                     dest='aws_session_token',
                                     help='AWS Session Token')

        # Create parameters
        aws_creation_params = aws_cmd_create_parser.add_argument_group(
            'Creation parameters')
        aws_creation_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                         default="ec2_ssrf",
                                         dest='vulnerable_app_id',
                                         help='Cumulonimbus vulnerable AWS application id')

        # Destroy parameters
        aws_destruction_params = aws_cmd_destroy_parser.add_argument_group(
            'Destruction parameters')
        aws_destruction_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                            default="ec2_ssrf",
                                            dest='vulnerable_app_id',
                                            help='Cumulonimbus vulnerable AWS application id')

        # Validate parameters
        aws_validate_params = aws_cmd_validate_parser.add_argument_group(
            'Validation parameters')
        aws_validate_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                         dest='vulnerable_app_id',
                                         help='Cumulonimbus vulnerable AWS application id')
        aws_validate_params.add_argument('--flag', action='store', required=True,
                                         dest='flag',
                                         help='The flag you captured')

        # Hint parameters
        aws_hint_params = aws_cmd_hint_parser.add_argument_group('Hint parameters')
        aws_hint_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                     dest='vulnerable_app_id',
                                     help='Cumulonimbus vulnerable AWS application id')
        aws_hint_params.add_argument('--level', action='store', type=int, choices=[1, 2, 3],
                                     default=1, dest='hint_level',
                                     help='Hint level: 1 = gentle nudge, 2 = moderate, 3 = explicit (default: 1)')

        # TTL parameters
        aws_ttl_params = aws_cmd_ttl_parser.add_argument_group('TTL parameters')
        aws_ttl_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                    dest='vulnerable_app_id',
                                    help='Cumulonimbus vulnerable AWS application id')
        aws_ttl_params.add_argument('--hours', action='store', type=float, required=True,
                                    dest='ttl_hours',
                                    help='Hours until the lab is automatically destroyed')

        aws_additional_parser = aws_parser.add_argument_group(
            'Additional arguments')
        aws_additional_parser.add_argument('-r',
                                           '--region',
                                           dest='region',
                                           nargs=1,
                                           help='Name of region to deploy resources to. Defaults to eu-west-1')

    def _init_azure_parser(self):
        azure_parser = self.subparsers.add_parser("azure",
                                                  parents=[
                                                      self.common_providers_args_parser],
                                                  help="Run {} against a Microsoft Azure account".format(global_variables.APP_NAME))

        azure_cmd_parser = azure_parser.add_subparsers(
            title="The command you want to run", dest="command", required=True,
            help="The command you want to run (authenticate, create, destroy, validate)")

        azure_cmd_auth_parser = azure_cmd_parser.add_parser(
            "authenticate", help="Authenticate {} against an Azure account".format(global_variables.APP_NAME))
        azure_cmd_create_parser = azure_cmd_parser.add_parser(
            "create", help="Create a vulnerable application in an Azure account")
        azure_cmd_destroy_parser = azure_cmd_parser.add_parser(
            "destroy", help="Destroy a vulnerable application in an Azure account")
        azure_cmd_validate_parser = azure_cmd_parser.add_parser(
            "validate", help="Validate a captured flag for an Azure application")
        azure_cmd_hint_parser = azure_cmd_parser.add_parser(
            "hint", help="Get a hint for an Azure application")
        azure_cmd_ttl_parser = azure_cmd_parser.add_parser(
            "ttl", help="Schedule auto-destroy for an Azure application")

        azure_auth_modes = azure_cmd_auth_parser.add_mutually_exclusive_group(
            required=True)

        azure_auth_modes.add_argument('--service-principal',
                                      action='store_true',
                                      help='Run {} with an Azure Service Principal'.format(global_variables.APP_NAME))

        azure_auth_s_params = azure_cmd_auth_parser.add_argument_group(
            'Authentication parameters for Service Principal')
        azure_auth_s_params.add_argument('--client-id',
                                         action='store',
                                         dest='client_id',
                                         help='Client ID of the service principal')
        azure_auth_s_params.add_argument('--client-secret',
                                         action='store',
                                         dest='client_secret',
                                         help='Client of the service principal')
        azure_auth_s_params.add_argument('--tenant-id',
                                         action='store',
                                         dest='tenant_id',
                                         help='ID of the Tenant (Directory) to scan')
        azure_auth_s_params.add_argument('--subscription-id',
                                         action='store',
                                         dest='subscription_id',
                                         help='Subscription context to deploy resources')

        # Create parameters
        azure_creation_params = azure_cmd_create_parser.add_argument_group(
            'Creation parameters')
        azure_creation_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                           default="sa_public_access",
                                           dest='vulnerable_app_id',
                                           help='Cumulonimbus vulnerable Azure application id')

        # Destroy parameters
        azure_destruction_params = azure_cmd_destroy_parser.add_argument_group(
            'Destruction parameters')
        azure_destruction_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                              default="sa_public_access",
                                              dest='vulnerable_app_id',
                                              help='Cumulonimbus vulnerable Azure application id')

        # Validate parameters
        azure_validate_params = azure_cmd_validate_parser.add_argument_group(
            'Validation parameters')
        azure_validate_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                           dest='vulnerable_app_id',
                                           help='Cumulonimbus vulnerable Azure application id')
        azure_validate_params.add_argument('--flag', action='store', required=True,
                                           dest='flag',
                                           help='The flag you captured')

        # Hint parameters
        azure_hint_params = azure_cmd_hint_parser.add_argument_group('Hint parameters')
        azure_hint_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                       dest='vulnerable_app_id',
                                       help='Cumulonimbus vulnerable Azure application id')
        azure_hint_params.add_argument('--level', action='store', type=int, choices=[1, 2, 3],
                                       default=1, dest='hint_level',
                                       help='Hint level: 1 = gentle nudge, 2 = moderate, 3 = explicit (default: 1)')

        # TTL parameters
        azure_ttl_params = azure_cmd_ttl_parser.add_argument_group('TTL parameters')
        azure_ttl_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                      dest='vulnerable_app_id',
                                      help='Cumulonimbus vulnerable Azure application id')
        azure_ttl_params.add_argument('--hours', action='store', type=float, required=True,
                                      dest='ttl_hours',
                                      help='Hours until the lab is automatically destroyed')

    def parse_args(self, args=None):
        args = self.parser.parse_args(args)
        if args is None:
            print('No arguments provided, try -h or --help to get additional information')
            return 1

        if not args.provider:
            self.parser.error(
                'You need to input a provider, try -h or --help to get additional information')

        if args.__dict__.get('fetch_local'):
            args.force_write = True

        v = vars(args)
        if v.get('provider') == 'aws':
            if not v.get('command'):
                self.parser.error(
                    'You need to input a command, try -h or --help to get additional information')
            if v.get('command') == 'authenticate':
                if not (v.get('aws_access_key_id') and v.get('aws_secret_access_key')):
                    self.parser.error(
                        'You need to provide an Access Key ID and Secret Access Key to authenticate')
                if v.get('aws_access_keys') and not (v.get('aws_access_key_id') or v.get('aws_secret_access_key')):
                    self.parser.error('When running with --access-keys, you must provide an Access Key ID '
                                      'and Secret Access Key.')
        elif v.get('provider') == 'azure':
            if v.get('service_principal') and not v.get('tenant_id') and not v.get('subscription_id'):
                self.parser.error(
                    'You must provide --tenant-id and --subscription-id when using --service-principal authentication')

        return args
