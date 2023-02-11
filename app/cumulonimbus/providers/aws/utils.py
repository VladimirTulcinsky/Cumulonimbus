#!/usr/bin/env python3
import cumulonimbus.global_variables as global_variables
import os


def get_caller_identity(session):
    sts_client = session.client("sts")
    identity = sts_client.get_caller_identity()
    return identity


def get_aws_account_id(session):
    caller_identity = get_caller_identity(session)
    account_id = caller_identity["Arn"].split(":")[4]
    return account_id


def get_partition_name(session):
    caller_identity = get_caller_identity(session)
    partition_name = caller_identity["Arn"].split(":")[1]
    return partition_name


def format_arn(partition, service, region, account_id, resource_id, resource_type=None):
    """
    Formats a resource ARN based on the parameters

    :param partition:                   The partition where the resource is located
    :param service:                     The service namespace that identified the AWS product
    :param region:                      The corresponding region
    :param account_id:                  The ID of the AWS account that owns the resource
    :param resource_id:                 The resource identified
    :param resource_type:               (Optional) The resource type
    :return:                            Resource ARN
    """

    try:
        # If a resource type is specified
        if resource_type is not None:
            arn = f"arn:{partition}:{service}:{region}:{account_id}:{resource_type}/{resource_id}"
        else:
            arn = f"arn:{partition}:{service}:{region}:{account_id}:{resource_id}"
    except Exception as e:
        print('Failed to parse a resource ARN: {}'.format(e))
        return None
    return arn


def get_path_to_aws_app(app_id):
    """
    Get the path to the AWS application.

    :param app_id:                      The application ID
    :return:                            The path to the application
    """
    return os.path.join(global_variables.ROOT_DIR, "applications/aws/{}/terraform".format(app_id))

def pretty_print_tf_output(app_id, output):
    """
    Get the value of a Terraform output.

    :param app_id:                      The application ID
    :param output:                      The output name
    :return:                            The output value
    """
    print("###############################################")
    print("#             Attacker Credentials            #")
    print("###############################################")
    print("[1] aws_access_key_id:" +
          output["attacker_aws_access_key_id"]["value"])
    print("[2] aws_secret_access_key:" +
          output["attacker_aws_secret_access_key"]["value"])
    print("These credentials are valid for the application: {}".format(app_id))
