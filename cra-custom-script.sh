#!/usr/bin/env bash

if [[ "${PIPELINE_DEBUG:-0}" == 1 ]]; then
    trap env EXIT
    env | sort
    set -x
fi

echo "[CRA Script] Removing Python 3.6..."
yum remove -yq python3.6

echo "[CRA Script] Installing Python 3.11..."
yum install -yq python3.11 python3.11-pip
unlink /usr/bin/python3
unlink /usr/bin/pip3
ln -s /usr/bin/python3.8 /usr/bin/python3
ln -s /usr/bin/pip3.8 /usr/bin/pip3

echo "[CRA Script] Upgrading pip..."
python3.11 -m pip install --upgrade pip || python3 -m pip install --upgrade pip

echo "Custom CRA Python setup script completed successfully."