#!/usr/bin/env python3
import os
import requests


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
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            ip = response.text.strip()
            cidr = ip + "/32"
            return cidr
    except:
        pass

    return "0.0.0.0/0"


public_ip = get_public_ip()
print(public_ip)


def init():
    global APP_NAME
    APP_NAME = "Cumulonimbus"

    global AWS_APP_LIST
    AWS_APP_LIST = get_aws_vulnerable_apps()

    global AZURE_APP_LIST
    AZURE_APP_LIST = get_azure_vulnerable_apps()

    global ROOT_DIR
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    global ATTACKER_PUBLIC_IP
    ATTACKER_PUBLIC_IP = get_public_ip()
