import re
import os
import cumulonimbus.global_variables as global_variables


def get_resource_group_name(id):
    return re.findall("/resourceGroups/(.*?)/", id)[0]


def get_path_to_azure_app(app_id):
    """
    Get the path to the AWS application.

    :param app_id:                      The application ID
    :return:                            The path to the application
    """
    return os.path.join(global_variables.ROOT_DIR, "applications/azure/{}/terraform".format(app_id))


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
    # TODO:
    print("These credentials are valid for the application: {}".format(app_id))
