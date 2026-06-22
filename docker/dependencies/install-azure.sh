#!/bin/bash
# Fail loudly: a failed install must fail the image build, not silently produce
# an image without `az` (which several Azure labs need for admin consent).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# =====================================
# Install the Azure CLI Tools
# =====================================

WORKDIR=/root
TMPDIR=/tmp
cd ${TMPDIR}

# Preferred version for reproducibility. Microsoft prunes old versions from the
# apt repo over time, so we fall back to the latest available rather than
# breaking the build on a version that has disappeared.
AZURE_CLI_VERSION="2.61.0"

echo -e "\n\nAzure CLI Installation Starting (preferred version ${AZURE_CLI_VERSION})...\n\n"

curl -sL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg

# Microsoft only publishes the azure-cli apt package for stable Debian/Ubuntu
# codenames (e.g. bookworm) — not for newer/testing ones like trixie, where the
# repo 404s. The package bundles its own Python, so the bookworm build runs fine
# on newer Debian bases too. Hardcode a supported codename rather than trusting
# the host's (which may be unsupported).
CLI_REPO="bookworm"

echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ ${CLI_REPO} main" \
    > /etc/apt/sources.list.d/azure-cli.list

apt-get update

if ! apt-get install -y --no-install-recommends "azure-cli=${AZURE_CLI_VERSION}-1~${CLI_REPO}"; then
    echo "Pinned azure-cli ${AZURE_CLI_VERSION} not available — installing the latest packaged version instead."
    apt-get install -y --no-install-recommends azure-cli
fi

# Verify the binary is actually present; fail the build if not.
if ! command -v az >/dev/null 2>&1; then
    echo "ERROR: Azure CLI installation failed — 'az' is not on PATH." >&2
    exit 1
fi

az --version | head -n 1 || true
echo -e "\n\nAzure CLI Installation Complete!\n\n"
