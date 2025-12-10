# ***************************************************************** #
# (C) Copyright IBM Corporation 2023.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #

# Test Build Version - icr.io/dsce-project/watsonx-generate-mkt-brief:v0.1-test
# Prod Build Version - icr.io/dsce-project/watsonx-generate-mkt-brief:v0.1-prod

ARG RUNTIME_BASE=registry.access.redhat.com/ubi9-minimal:latest

FROM ${RUNTIME_BASE} as base

# Args for artifactory credentials
ARG SERVICE_PORT=8050
ENV SERVICE_PORT ${SERVICE_PORT}

# Setting up the working directory
WORKDIR /app

# Installing the required python library to run models
COPY requirements.txt /app/requirements.txt

RUN microdnf update -y && \
    microdnf install -y python3.11 python3.11-pip && \
    microdnf clean all

RUN ln -s /usr/bin/python3.11 /usr/bin/python3 && \
    ln -s /usr/bin/pip3.11 /usr/bin/pip3

RUN python3 --version > /app/python-version.txt
RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

COPY assets /app/assets
COPY payload /app/payload
COPY analytics.py /app/analytics.py
COPY app-config.properties /app/app-config.properties
COPY sample-brief-gen.txt /app/sample-brief-gen.txt
COPY template.py /app/template.py

EXPOSE ${SERVICE_PORT}

ENTRYPOINT ["python3","template.py"]
