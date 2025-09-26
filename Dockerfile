FROM registry.sensetime.com/zoetrope/library/ubuntu:20.04

# Install apt packages
RUN apt-get update && \
    apt-get install -y \
        wget curl git vim \
        make \
    && \
    apt-get autoclean

# Set timezone
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -yq tzdata && \
    dpkg-reconfigure -f noninteractive tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    apt-get autoclean

# Install Python 3.10 from deadsnakes PPA
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
        python3.10 \
        python3.10-dev \
        python3.10-venv \
        python3-pip && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.10 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip cache purge

# Update PATH to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# COPY pyproject.toml and export requirements
COPY pyproject.toml /opt/pyproject.toml
RUN cd /opt && \
    /opt/venv/bin/pip install toml-to-requirements && \
    toml-to-req --toml-file pyproject.toml --optional-lists dev && \
    /opt/venv/bin/pip install -r requirements.txt && \
    /opt/venv/bin/pip cache purge

# COPY code
COPY . /workspace/web-backend
# Install code
RUN cd /workspace/web-backend && \
    /opt/venv/bin/pip install . && \
    /opt/venv/bin/pip cache purge

# Set working directory
WORKDIR /workspace/web-backend

# Set environment variables for MongoDB admin credentials
ENV MONGODB_ADMIN_USERNAME=admin
ENV MONGODB_ADMIN_PASSWORD=

# Set entrypoint
ENTRYPOINT ["/opt/venv/bin/python", "main.py"]
