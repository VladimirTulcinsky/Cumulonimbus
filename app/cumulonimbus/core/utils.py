import cumulonimbus.global_variables as global_variables
import os


def get_relative_path(relative_path):
    return os.path.join(global_variables.ROOT_DIR, relative_path)


def get_key_pair_path(key_name):
    return os.path.join(get_relative_path('.data/.ssh/'), key_name)


def create_data_directory():
    if not os.path.isdir(os.path.join(global_variables.ROOT_DIR, '.data')):
        dirs = [
            '.data',
            '.data/.ssh',
            '.data/.azure',
            '.data/.aws'
        ]
        for dir_path in dirs:
            full_path = os.path.join(global_variables.ROOT_DIR, dir_path)
            os.makedirs(full_path, exist_ok=True)
