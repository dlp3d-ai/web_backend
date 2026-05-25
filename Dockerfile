FROM ubuntu:20.04

# Install apt packages
RUN apt-get update && \
    apt-get install -y \
        ca-certificates curl git vim \
        unzip \
    && \
    apt-get autoclean

# Set timezone
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -yq tzdata && \
    dpkg-reconfigure -f noninteractive tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    apt-get autoclean

# Install uv and managed Python 3.10.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_PYTHON_INSTALL_DIR=/opt/uv-python
RUN uv python install 3.10.12

# Download protoc
RUN mkdir -p /opt/protoc && cd /opt/protoc && \
    curl -LjO https://github.com/protocolbuffers/protobuf/releases/download/v31.1/protoc-31.1-linux-x86_64.zip \
    && unzip protoc-31.1-linux-x86_64.zip \
    && rm -f protoc-31.1-linux-x86_64.zip \
    && chmod +x bin/protoc && \
    ln -s /opt/protoc/bin/protoc /usr/bin/protoc && \
    protoc --version

# Create virtual environment
RUN uv venv --python 3.10.12 /opt/venv && \
    uv pip install --python /opt/venv/bin/python --upgrade pip setuptools wheel && \
    uv cache clean

# Update PATH to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# COPY pyproject.toml, export requirements, and install dependencies
COPY pyproject.toml /opt/pyproject.toml
RUN cd /opt && \
    uv pip install --python /opt/venv/bin/python toml-to-requirements && \
    toml-to-req --toml-file pyproject.toml --optional-lists dev && \
    uv pip install --python /opt/venv/bin/python -r requirements.txt && \
    uv cache clean

# COPY code
COPY . /workspace/web-backend
# Install code
RUN cd /workspace/web-backend && \
    uv pip install --python /opt/venv/bin/python . && \
    uv cache clean

# Set working directory
WORKDIR /workspace/web-backend

# Set environment variables for MongoDB
ENV MONGODB_HOST=mongodb
ENV MONGODB_PORT=27017
ENV MONGODB_ADMIN_USERNAME=admin
ENV MONGODB_ADMIN_PASSWORD=
ENV MONGODB_USERNAME=web_user
ENV MONGODB_PASSWORD=web_password
ENV MONGODB_DATABASE=web_database
ENV MONGODB_AUTH_DATABASE=web_database

# Set entrypoint
ENTRYPOINT ["/opt/venv/bin/python", "main.py", "--config_path", "configs/community.py"]
