import re
import os
import cumulonimbus.global_variables as global_variables


def get_resource_group_name(id):
    return re.findall("/resourceGroups/(.*?)/", id)[0]


def get_path_to_azure_app(app_id):
    """
    Get the path to the Azure application.

    :param app_id:                      The application ID
    :return:                            The path to the application
    """
    return os.path.join(global_variables.ROOT_DIR, "applications/azure/{}/terraform".format(app_id))
