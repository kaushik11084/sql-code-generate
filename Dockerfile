# ***************************************************************** #
# (C) Copyright IBM Corporation 2023.                               #
#                                                                   #
# The source code for this program is not published or otherwise    #
# divested of its trade secrets, irrespective of what has been      #
# deposited with the U.S. Copyright Office.                         #
# ***************************************************************** #

# Test Build Version - icr.io/dsce-project/watsonx-nl2sql:v0.1-test
# Prod Build Version - icr.io/dsce-project/watsonx-nl2sql:v0.1-prod

ARG RUNTIME_BASE=registry.access.redhat.com/ubi8/ubi-minimal:8.8-1014

FROM ${RUNTIME_BASE} as base

# Args for artifactory credentials
ARG SERVICE_PORT=8050
ENV SERVICE_PORT ${SERVICE_PORT}

# Setting up the working directory
WORKDIR /app


# ------------------------------------------------------------
# Install Python 3.11 + pip safely (avoid pip==22.3 resolver bug)
# ------------------------------------------------------------
RUN microdnf install -y python3.11 python3.11-pip && microdnf clean all

# Upgrade pip to a modern resolver
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# ------------------------------------------------------------
# FIX CRITICAL ISSUE: Remove urllib3==1.26.18 if present
# because ibm-cloud-sdk-core>=3.21 requires urllib3>=2.1.0
# ------------------------------------------------------------
COPY requirements.txt /app/requirements.txt
RUN sed -i '/urllib3==/d' requirements.txt

# Install Python dependencies
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# Copy application code
# ------------------------------------------------------------
COPY assets /app/assets
COPY payload /app/payload
COPY analytics.py /app/analytics.py
COPY app-config.properties /app/app-config.properties
COPY template.py /app/template.py

EXPOSE ${SERVICE_PORT}

ENTRYPOINT ["python3","template.py"]