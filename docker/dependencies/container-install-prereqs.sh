#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# =====================================
# install software packages needed for
# all the other components to run
# =====================================

WORKDIR=/root
TMPDIR=/tmp
cd ${TMPDIR}

echo -e "\n\nSoftware Pre-reqs Installation Starting...\n\n"

# =====================================
# set up the pre-reqs
# =====================================
apt-get update > /dev/null 2>&1
apt-get install -qy \
  apt-transport-https \
  apt-utils \
  ca-certificates \
  curl \
  gnupg \
  jq \
  less \
  nano \
  python3 \
  python3-pip \
  tzdata \
  vim \
  sqlite3 \
  lsb-release \

apt-get update && apt-get install -y gnupg software-properties-common wget
wget -qO - https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
apt-get update
apt-get install -y terraform


  

pip3 install boto3 \
  python-terraform \
  requests \
  python-dotenv \
  azure-identity

echo -e "\n\nSoftware Pre-reqs Installation Complete!\n\n"

#  unzip \
#  virtualenv \
#  virtualenvwrapper \
#  cmake \

#  groff \
#  dialog \
#  wget \