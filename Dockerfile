# ***************************************************************** #
# (C) Copyright IBM Corporation 2023.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #

# Test Build Version - icr.io/dsce-project/watsonx-generate-mkt-brief:v0.1-test
# Prod Build Version - icr.io/dsce-project/watsonx-generate-mkt-brief:v0.1-prod

ARG RUNTIME_BASE=registry.access.redhat.com/ubi9-minimal:9.7

FROM ${RUNTIME_BASE} as base

# Args for artifactory credentials
ARG SERVICE_PORT=8050
ENV SERVICE_PORT ${SERVICE_PORT}

# Setting up the working directory
WORKDIR /app

# Copy requirements first (pip caching optimization)
COPY requirements.txt /app/requirements.txt
COPY cra-custom-script.sh /app/cra-custom-script.sh

# Install Python 3.11 and tools (DL3041, DL3059 fixes)
RUN microdnf update -y && \
    microdnf install -y \
        python3.11 \
        python3.11-pip \
        findutils && \
    ln -s /usr/bin/python3.11 /usr/bin/python3 && \
    ln -s /usr/bin/pip3.11 /usr/bin/pip3 && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    microdnf clean all

# Write versions
RUN python3 --version > /app/python-version.txt
RUN pip --version > /app/pip-version.txt

# Install Python dependencies (DL3042 fix)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the app
COPY assets /app/assets
COPY payload /app/payload
COPY analytics.py /app/analytics.py
COPY app-config.properties /app/app-config.properties
COPY sample-brief-gen.txt /app/sample-brief-gen.txt
COPY template.py /app/template.py

EXPOSE ${SERVICE_PORT}

ENTRYPOINT ["python3","template.py"]
