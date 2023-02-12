#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv


def get_aws_vulnerable_apps():
    directory = './cumulonimbus/applications/aws/'
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    return directories


def get_azure_vulnerable_apps():
    directory = './cumulonimbus/applications/azure/'
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    return directories


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            return {"azure": ip, "aws": f"{ip}/32"}
    except:
        pass
    return {"azure": "0.0.0.0/0", "aws": "0.0.0.0/0"}


def __init_general():
    global APP_NAME
    APP_NAME = "Cumulonimbus"

    global ROOT_DIR
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    global ATTACKER_PUBLIC_IP
    ATTACKER_PUBLIC_IP = get_public_ip()


def __init_aws():
    global AWS_APP_LIST
    AWS_APP_LIST = get_aws_vulnerable_apps()

    global PATH_TO_AWS_CREDENTIALS
    PATH_TO_AWS_CREDENTIALS = os.path.join(ROOT_DIR, ".data/.aws/credentials")

    global PATH_TO_AWS_CONFIG
    PATH_TO_AWS_CONFIG = os.path.join(ROOT_DIR, ".data/.aws/config")

    # Set the env variable to our .data/.aws folder for boto to read from
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = PATH_TO_AWS_CREDENTIALS
    os.environ['AWS_CONFIG_FILE'] = PATH_TO_AWS_CONFIG


def __init_azure():
    global AZURE_APP_LIST
    AZURE_APP_LIST = get_azure_vulnerable_apps()

    global PATH_TO_AZURE_CREDENTIALS
    PATH_TO_AZURE_CREDENTIALS = os.path.join(ROOT_DIR, ".data/.env")

    load_dotenv(PATH_TO_AZURE_CREDENTIALS)


def init():
    # GENERAL
    __init_general()

    # AWS
    __init_aws()

    # AZURE
    __init_azure()
