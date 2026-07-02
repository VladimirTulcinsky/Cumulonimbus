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
  openssh-client \

apt-get install -qy unzip wget

TERRAFORM_VERSION=1.9.8
wget -q "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -O /tmp/terraform.zip
unzip -q /tmp/terraform.zip -d /usr/local/bin/
rm /tmp/terraform.zip
chmod +x /usr/local/bin/terraform

# crane — pull and inspect OCI/Docker images from a registry WITHOUT a Docker
# daemon (the acr image lab dissects images via AcrPull; this container has no
# Docker). Single static binary.
wget -q "https://github.com/google/go-containerregistry/releases/latest/download/go-containerregistry_Linux_x86_64.tar.gz" -O /tmp/crane.tar.gz \
  && tar -xzf /tmp/crane.tar.gz -C /usr/local/bin crane \
  && rm -f /tmp/crane.tar.gz \
  && chmod +x /usr/local/bin/crane


  

pip3 install boto3 \
  python-terraform \
  requests \
  python-dotenv \
  azure-identity \
  playwright

playwright install-deps chromium
playwright install chromium

echo -e "\n\nSoftware Pre-reqs Installation Complete!\n\n"

#  unzip \
#  virtualenv \
#  virtualenvwrapper \
#  cmake \

#  groff \
#  dialog \
#  wget \