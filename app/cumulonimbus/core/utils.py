import cumulonimbus.global_variables as global_variables
import json
import os
import random
import re


def get_relative_path(relative_path):
    return os.path.join(global_variables.ROOT_DIR, relative_path)


def get_session_file():
    return os.path.join(global_variables.ROOT_DIR, '.data', 'session.json')


# The session name suffix has two parts: a human-chosen label and a short
# random tag appended for uniqueness, so two people who pick the same label
# (e.g. both "vt") still get distinct resource names. Both are kept short
# because the suffix is appended to length-constrained cloud resource names
# (e.g. AWS IAM names and Entra mail nicknames cap at 64 chars, on top of each
# lab's base name).
NAME_SUFFIX_LABEL_MAX = 8
NAME_SUFFIX_TAG_LENGTH = 4
_TAG_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"


def sanitize_name_label(value):
    """Normalise the human-chosen part of a session name into a token safe to
    embed in cloud resource names (lowercase alphanumeric, capped length).
    Returns '' if nothing usable remains."""
    if not value:
        return ''
    return re.sub(r'[^a-z0-9]', '', str(value).lower())[:NAME_SUFFIX_LABEL_MAX]


def _random_tag():
    return ''.join(random.choice(_TAG_ALPHABET) for _ in range(NAME_SUFFIX_TAG_LENGTH))


def set_name_suffix(value):
    """Persist the per-player name suffix used to namespace resources.

    The stored suffix is the sanitized human label plus a short random tag, so
    two people sharing one tenant/account who pick the same label still get
    distinct resource names. The tag is generated once and stays stable for a
    given label on this install, so create and destroy produce matching names.
    Returns the full suffix ('' when no usable label was given)."""
    label = sanitize_name_label(value)
    path = get_session_file()
    data = {}
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
        except (ValueError, OSError):
            data = {}

    if not label:
        suffix = ''
    elif data.get('session_label') == label and data.get('name_suffix'):
        # Same label as before — keep the existing tag so names stay stable.
        suffix = data['name_suffix']
    else:
        suffix = label + _random_tag()

    data['session_label'] = label
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
