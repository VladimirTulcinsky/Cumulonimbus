#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# =====================================
# install the AWS CLI Tools
# =====================================
TMPDIR=/tmp

echo -e "\n\nAWS2 CLI Installation Starting...\n\n"

# =====================================
# install AWS CLI v2
# =====================================
cd ${TMPDIR}
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install --update

# =====================================
# clean up install artifacts
# =====================================
rm ${TMPDIR}/awscliv2.zip
rm -rf ${TMPDIR}/aws


