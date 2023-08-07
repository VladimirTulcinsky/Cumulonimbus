#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# =====================================
# install the Azure CLI Tools
# =====================================

WORKDIR=/root
TMPDIR=/tmp
cd ${TMPDIR}

echo -e "\n\nAzure CLI Installation Starting...\n\n"

curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg

CLI_REPO=$(lsb_release -cs)

echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ ${CLI_REPO} main" \
    > /etc/apt/sources.list.d/azure-cli.list

apt-get update && apt-get install -y azure-cli

az upgrade -y

echo -e "\n\nAzure CLI Installation Complete!\n\n"
