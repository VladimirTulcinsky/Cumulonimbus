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

apt-get install -qy unzip wget

TERRAFORM_VERSION=1.9.8
wget -q "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -O /tmp/terraform.zip
unzip -q /tmp/terraform.zip -d /usr/local/bin/
rm /tmp/terraform.zip
chmod +x /usr/local/bin/terraform


  

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