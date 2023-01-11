#!/usr/bin/env python3
import argparse
import cumulonimbus.global_variables as global_variables


class CumulonimbusParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            epilog='To get additional help on a specific provider run: {}.py <provider> -h'.format(global_variables.app_name))

        self.common_providers_args_parser = argparse.ArgumentParser(
            add_help=False)

        self.subparsers = self.parser.add_subparsers(title="The provider you want to run {} against".format(global_variables.app_name),
                                                     dest="provider")

        self._init_aws_parser()
        self._init_azure_parser()

    def _init_aws_parser(self):
        aws_parser = self.subparsers.add_parser("aws",
                                                parents=[
                                                    self.common_providers_args_parser],
                                                help="Run {} against an Amazon Web Services account".format(global_variables.app_name))

        aws_cmd_parser = aws_parser.add_subparsers(title="The command you want to run",
                                                   dest="command")

        # Possible commands: authenticate, create
        aws_cmd_auth_parser = aws_cmd_parser.add_parser(
            "authenticate", help="Authenticate {} against an Amazon Web Services account".format(global_variables.app_name))
        aws_cmd_create_parser = aws_cmd_parser.add_parser(
            "create", help="Create a vulnerable application in an Amazon Web Services account".format(global_variables.app_name))

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

        # Vulnerable application creation parameters
        aws_creation_params = aws_cmd_create_parser.add_argument_group(
            'Creation parameters')
        aws_creation_params.add_argument('--app-id', action='store', choices=global_variables.aws_app_list, required=True,
                                         default="ec2_ssrf",
                                         dest='vulnerable_app_id',
                                         help='Cumulonimbus vulnerable AWS application id')

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
                                                  help="Run {} against a Microsoft Azure account".format(global_variables.app_name))

        azure_cmd_parser = azure_parser.add_subparsers(
            title="The command you want to run", dest="command", required=True, help="The command you want to run (authenticate, create, etc.)")

        # Possible commands: authenticate, create
        azure_cmd_auth_parser = azure_cmd_parser.add_parser(
            "authenticate", help="Authenticate {} against an Azure account".format(global_variables.app_name))
        azure_cmd_create_parser = azure_cmd_parser.add_parser(
            "create", help="Create a vulnerable application in an Azure account".format(global_variables.app_name))

        azure_auth_modes = azure_cmd_auth_parser.add_mutually_exclusive_group(
            required=True)

        # Authentication parameters
        # username/password authentication
        azure_auth_modes.add_argument('--user-account',
                                      action='store_true',
                                      help='Run Cumulonimbus with user credentials')

        # Service Principal authentication
        azure_auth_modes.add_argument('--service-principal',
                                      action='store_true',
                                      help='Run {} with an Azure Service Principal'.format(global_variables.app_name))

        azure_auth_u_params = azure_cmd_auth_parser.add_argument_group(
            'Authentication parameters for User Account')

        azure_auth_u_params.add_argument('-u',
                                         '--username',
                                         action='store',
                                         default=None,
                                         dest='username',
                                         help='Username of the Azure account')
        azure_auth_u_params.add_argument('-p',
                                         '--password',
                                         action='store',
                                         default=None,
                                         dest='password',
                                         help='Password of the Azure account')

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
        azure_auth_s_params.add_argument('--tenant',
                                         action='store',
                                         dest='tenant_id',
                                         help='ID of the Tenant (Directory) to scan')

        # Additional arguments

        """ azure_scope.add_argument('--subscription',
                                 action='store',
                                 default="",
                                 nargs='+',
                                 dest='subscription_id',
                                 help='IDs (separated by spaces) of the Azure subscription(s) to scan. '
                                      'By default, only the default subscription will be scanned.') """

        # Vulnerable application creation parameters
        azure_creation_params = azure_cmd_create_parser.add_argument_group(
            'Creation parameters')
        azure_creation_params.add_argument('--app-id', action='store', choices=global_variables.azure_app_list, required=True,
                                           default="vm_prt",
                                           dest='vulnerable_app_id',
                                           help='Cumulonimbus vulnerable Azure application id')

    def parse_args(self, args=None):
        args = self.parser.parse_args(args)

        # Cannot simply use required for backward compatibility
        if not args.provider:
            self.parser.error('You need to input a provider')

        # If local analysis, overwrite results
        if args.__dict__.get('fetch_local'):
            args.force_write = True

        # Test conditions
        v = vars(args)
        # AWS
        if v.get('provider') == 'aws':
            if v.get('aws_access_keys') and not (v.get('aws_access_key_id') or v.get('aws_secret_access_key')):
                self.parser.error('When running with --access-keys, you must provide an Access Key ID '
                                  'and Secret Access Key.')
        # Azure
        elif v.get('provider') == 'azure':
            if v.get('tenant_id') and not (v.get('service_principal') or v.get('user_account_browser') or v.get('user_account')):
                self.parser.error('--tenant can only be set when using --user-account-browser or --user-account or '
                                  '--service-principal authentication')
            if v.get('service_principal') and not v.get('tenant_id'):
                self.parser.error(
                    'You must provide --tenant when using --service-principal authentication')
            if v.get('user_account') and not v.get('tenant_id'):
                self.parser.error(
                    'You must provide --tenant when using --user-account authentication')
            # check the value of 'mode' argument and display the relevant group arguments
            if v.get('mode') == 'sp':
                print("Arguments from Group 1")
            elif v.get('mode') == 'user':
                print("Arguments from Group 2")
