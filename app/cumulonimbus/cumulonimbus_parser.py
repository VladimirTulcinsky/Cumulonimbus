#!/usr/bin/env python3
import argparse
import sys
import cumulonimbus.global_variables as global_variables


AWS_REGIONS = [
    'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
    'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
    'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2',
    'ca-central-1', 'sa-east-1',
]

AZURE_REGIONS = [
    'West Europe', 'North Europe',
    'East US', 'East US 2', 'West US', 'West US 2', 'West US 3', 'Central US',
    'UK South', 'UK West',
    'Southeast Asia', 'East Asia',
    'Australia East', 'Australia Southeast',
    'Canada Central', 'Brazil South',
    'Japan East', 'France Central',
    'Germany West Central', 'Switzerland North', 'Norway East',
]


class _RegionEnrichedParser(argparse.ArgumentParser):
    """ArgumentParser that appends the allowed region list to any --region error."""

    def error(self, message):
        if '--region' in message or ('-r' in message and 'region' in message.lower()):
            # Detect provider by inspecting registered choices on the region action
            region_action = next(
                (a for a in self._actions if getattr(a, 'dest', '') == 'region'),
                None,
            )
            choices = getattr(region_action, 'choices', None) or []
            if choices:
                col_width = max(len(r) for r in choices) + 2
                cols = 3
                lines = []
                row = []
                for i, r in enumerate(choices):
                    row.append(r.ljust(col_width))
                    if len(row) == cols:
                        lines.append('  ' + ''.join(row))
                        row = []
                if row:
                    lines.append('  ' + ''.join(row))
                region_hint = '\nAllowed --region values:\n' + '\n'.join(lines) + '\n'
                sys.stderr.write(region_hint + '\n')
        super().error(message)


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
                                                   dest="command",
                                                   required=True,
                                                   parser_class=_RegionEnrichedParser)

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
        aws_cmd_parser.add_parser(
            "list", help="List available Amazon Web Services lab IDs")

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
        aws_auth_params.add_argument('-r', '--region',
                                     action='store',
                                     required=True,
                                     choices=AWS_REGIONS,
                                     metavar='REGION',
                                     dest='region',
                                     help='AWS region to deploy resources to. Allowed values: ' + ', '.join(AWS_REGIONS))
        aws_auth_params.add_argument('--session-name',
                                     action='store',
                                     default=None,
                                     dest='name_suffix',
                                     help='Optional per-player identifier used to namespace deployed resources, so multiple users can share one account without collisions. Letters/digits only, max 12 chars (e.g. your initials or team name)')

        # Create parameters
        aws_creation_params = aws_cmd_create_parser.add_argument_group('Creation parameters')
        aws_creation_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                         dest='vulnerable_app_id',
                                         help='Cumulonimbus vulnerable AWS application id')

        # Destroy parameters
        aws_destruction_params = aws_cmd_destroy_parser.add_argument_group('Destruction parameters')
        aws_destruction_params.add_argument('--app-id', action='store', choices=global_variables.AWS_APP_LIST, required=True,
                                            dest='vulnerable_app_id',
                                            help='Cumulonimbus vulnerable AWS application id')

        # Validate parameters
        aws_validate_params = aws_cmd_validate_parser.add_argument_group('Validation parameters')
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

    def _init_azure_parser(self):
        azure_parser = self.subparsers.add_parser("azure",
                                                  parents=[
                                                      self.common_providers_args_parser],
                                                  help="Run {} against a Microsoft Azure account".format(global_variables.APP_NAME))

        azure_cmd_parser = azure_parser.add_subparsers(
            title="The command you want to run", dest="command", required=True,
            help="The command you want to run (authenticate, create, destroy, validate, hint, ttl, list)",
            parser_class=_RegionEnrichedParser)

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
        azure_cmd_parser.add_parser(
            "list", help="List available Azure lab IDs")

        azure_auth_modes = azure_cmd_auth_parser.add_mutually_exclusive_group(required=True)
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
                                         help='Client secret of the service principal')
        azure_auth_s_params.add_argument('--tenant-id',
                                         action='store',
                                         dest='tenant_id',
                                         help='ID of the Tenant (Directory) to scan')
        azure_auth_s_params.add_argument('--subscription-id',
                                         action='store',
                                         dest='subscription_id',
                                         help='Subscription context to deploy resources')
        azure_auth_s_params.add_argument('--tenant-domain',
                                         action='store',
                                         dest='tenant_domain',
                                         help='Primary domain of the Azure AD tenant (e.g. contoso.onmicrosoft.com)')
        azure_auth_s_params.add_argument('-r', '--region',
                                         action='store',
                                         required=True,
                                         choices=AZURE_REGIONS,
                                         metavar='REGION',
                                         dest='region',
                                         help='Azure region to deploy resources to. Allowed values: ' + ', '.join(AZURE_REGIONS))
        azure_auth_s_params.add_argument('--session-name',
                                         action='store',
                                         default=None,
                                         dest='name_suffix',
                                         help='Optional per-player identifier used to namespace deployed resources, so multiple users can share one tenant without collisions. Letters/digits only, max 12 chars (e.g. your initials or team name)')

        # Create parameters
        azure_creation_params = azure_cmd_create_parser.add_argument_group('Creation parameters')
        azure_creation_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                           dest='vulnerable_app_id',
                                           help='Cumulonimbus vulnerable Azure application id')

        # Destroy parameters
        azure_destruction_params = azure_cmd_destroy_parser.add_argument_group('Destruction parameters')
        azure_destruction_params.add_argument('--app-id', action='store', choices=global_variables.AZURE_APP_LIST, required=True,
                                              dest='vulnerable_app_id',
                                              help='Cumulonimbus vulnerable Azure application id')

        # Validate parameters
        azure_validate_params = azure_cmd_validate_parser.add_argument_group('Validation parameters')
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
            if v.get('command') == 'authenticate':
                if not (v.get('aws_access_key_id') and v.get('aws_secret_access_key')):
                    self.parser.error(
                        'You need to provide an Access Key ID and Secret Access Key to authenticate')
        elif v.get('provider') == 'azure':
            if v.get('service_principal'):
                missing = [f'--{f}' for f in ('tenant_id', 'subscription_id', 'tenant_domain') if not v.get(f)]
                if missing:
                    self.parser.error(
                        f'You must provide {", ".join(missing)} when using --service-principal authentication')

        return args
