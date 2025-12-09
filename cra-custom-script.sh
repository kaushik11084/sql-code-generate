#!/usr/bin/env bash

###############################################
# Enable CRA pipeline debug output
###############################################
if [[ "${PIPELINE_DEBUG:-0}" == 1 ]]; then
    trap env EXIT
    env | sort
    set -x
fi

###############################################
# Desired Python version (CUSTOMIZE HERE)
###############################################
PY_VERSION=3.11
# Allowed: 3.8, 3.9, 3.10, 3.11

###############################################
# Ensure dnf is available (ubi8-minimal only has microdnf)
###############################################
if ! command -v dnf >/dev/null 2>&1; then
    echo "Installing dnf..."
    microdnf install -y dnf && microdnf clean all
fi

###############################################
# Remove default Python if installed
###############################################
if rpm -q python36 >/dev/null 2>&1; then
    echo "Removing default Python 3.6 packages..."
    dnf remove -y python36 python36-libs python36-pip || true
fi

###############################################
# Install desired Python version
###############################################
echo "Installing Python ${PY_VERSION}..."
dnf install -y python${PY_VERSION} python${PY_VERSION}-pip

###############################################
# Recreate python3 and pip3 symlinks
###############################################
echo "Updating python3 and pip3 symlinks..."
rm -f /usr/bin/python3
rm -f /usr/bin/pip3

ln -s /usr/bin/python${PY_VERSION} /usr/bin/python3
ln -s /usr/bin/pip${PY_VERSION} /usr/bin/pip3

###############################################
# Upgrade pip to a modern version
###############################################
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

###############################################
# Confirmation
###############################################
echo "Python installed:"
python3 --version

echo "Pip installed:"
pip3 --version

echo "Custom CRA Python setup script completed successfully."

