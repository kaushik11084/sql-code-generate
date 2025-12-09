#!/usr/bin/env bash

if [[ "${PIPELINE_DEBUG:-0}" == 1 ]]; then
    trap env EXIT
    env | sort
    set -x

microdnf install -y dnf

microdnf -y clean all

microdnf remove -y python36 python36-libs python36-pip && microdnf clean all

microdnf install -y python3.11 python3.11-pip

python3 -m pip install --upgrade pip

echo "Custom CRA Python setup script completed successfully."