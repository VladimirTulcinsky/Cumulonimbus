#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# =====================================
# Install the Azure CLI Tools
# =====================================

WORKDIR=/root
TMPDIR=/tmp
cd ${TMPDIR}

# Pinned version — update intentionally, not via az upgrade
AZURE_CLI_VERSION="2.61.0"

echo -e "\n\nAzure CLI Installation Starting (version ${AZURE_CLI_VERSION})...\n\n"

curl -sL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg

CLI_REPO=$(lsb_release -cs)

echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ ${CLI_REPO} main" \
    > /etc/apt/sources.list.d/azure-cli.list

apt-get update && apt-get install -y --no-install-recommends \
    azure-cli=${AZURE_CLI_VERSION}-1~${CLI_REPO}

echo -e "\n\nAzure CLI Installation Complete!\n\n"
