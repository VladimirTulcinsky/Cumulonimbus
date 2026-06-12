import cumulonimbus.global_variables as global_variables
import json
import os
import re


def get_relative_path(relative_path):
    return os.path.join(global_variables.ROOT_DIR, relative_path)


def get_session_file():
    return os.path.join(global_variables.ROOT_DIR, '.data', 'session.json')


# Max length of a session name once normalised. Kept short because the suffix
# is appended to length-constrained cloud resource names (e.g. AWS IAM names
# and Entra mail nicknames cap at 64 chars, on top of each lab's base name).
NAME_SUFFIX_MAX_LENGTH = 12


def sanitize_name_suffix(value):
    """Normalise a player/team identifier into a token that is safe to embed in
    cloud resource names (lowercase alphanumeric, capped length)."""
    if not value:
        return ''
    token = re.sub(r'[^a-z0-9]', '', str(value).lower())
    return token[:NAME_SUFFIX_MAX_LENGTH]


def set_name_suffix(value):
    """Persist the per-player name suffix so subsequent create/destroy commands
    namespace their resources consistently. Returns the sanitized value."""
    suffix = sanitize_name_suffix(value)
    path = get_session_file()
    data = {}
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
        except (ValueError, OSError):
            data = {}
    data['name_suffix'] = suffix
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return suffix


def get_name_suffix():
    """Return the persisted per-player name suffix, or '' if none is set."""
    path = get_session_file()
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f).get('name_suffix', '') or ''
        except (ValueError, OSError):
            return ''
    return ''


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
