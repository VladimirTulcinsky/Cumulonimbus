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
    global app_name
    app_name = "Cumulonimbus"

    global aws_app_list
    aws_app_list = get_aws_vulnerable_apps()

    global azure_app_list
    azure_app_list = get_azure_vulnerable_apps()
