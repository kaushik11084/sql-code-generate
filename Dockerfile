# ***************************************************************** #
# (C) Copyright IBM Corporation 2023.                               #
# ***************************************************************** #

ARG RUNTIME_BASE=registry.access.redhat.com/ubi8/ubi-minimal:8.8-1014
FROM ${RUNTIME_BASE} as base

ARG SERVICE_PORT=8050
ENV SERVICE_PORT=${SERVICE_PORT}

WORKDIR /app

# ---------------------------------------------------
# Install Python 3.10 properly on UBI8 minimal
# ---------------------------------------------------
RUN microdnf install -y dnf && \
    dnf install -y python3.10 python3.10-pip && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/bin/pip3.10 /usr/bin/pip && \
    python3 -m ensurepip --upgrade && \
    pip install --upgrade pip setuptools wheel && \
    dnf clean all && rm -rf /var/cache/dnf

# ---------------------------------------------------
# Install application dependencies
# ---------------------------------------------------
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------------------------------------------------
# Copy application source
# ---------------------------------------------------
COPY assets /app/assets
COPY payload /app/payload
COPY analytics.py /app/analytics.py
COPY app-config.properties /app/app-config.properties
COPY sample-brief-gen.txt /app/sample-brief-gen.txt
COPY template.py /app/template.py

EXPOSE ${SERVICE_PORT}

ENTRYPOINT ["python3", "template.py"]
