#!/usr/bin/env python3
import os


def get_aws_vulnerable_apps():
    directory = './cumulonimbus/applications/aws/'
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    return directories


def get_azure_vulnerable_apps():
    directory = './cumulonimbus/applications/azure/'
    directories = [f.name for f in os.scandir(directory) if f.is_dir()]
    return directories


def init():
    global APP_NAME
    APP_NAME = "Cumulonimbus"

    global AWS_APP_LIST
    AWS_APP_LIST = get_aws_vulnerable_apps()

    global AZURE_APP_LIST
    AZURE_APP_LIST = get_azure_vulnerable_apps()

    global ROOT_DIR
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
