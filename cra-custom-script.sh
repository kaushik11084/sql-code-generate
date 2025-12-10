#!/usr/bin/env bash

if [[ "${PIPELINE_DEBUG:-0}" == 1 ]]; then
    trap env EXIT
    env | sort
    set -x
fi

echo "[CRA Script] Installing dnf..."
microdnf install -y dnf
microdnf -y clean all

echo "[CRA Script] Removing Python 3.6..."
microdnf remove -y python36 python36-libs python36-pip || true
microdnf clean all

echo "[CRA Script] Installing Python 3.11..."
microdnf install -y python3.11 python3.11-pip

echo "[CRA Script] Upgrading pip..."
python3.11 -m pip install --upgrade pip || python3 -m pip install --upgrade pip

echo "Custom CRA Python setup script completed successfully."