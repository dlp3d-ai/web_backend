
# Docker Deployment Guide

## Table of Contents

- [Overview](#overview)
- [GPU Acceleration](#gpu-acceleration)
- [Network Proxy Configuration](#network-proxy-configuration)
- [Standalone Web Backend Service](#standalone-web-backend-service)
- [Building from Source](#building-from-source)

## Overview

This guide covers advanced Docker deployment options for the DLP3D Web Backend service, including GPU acceleration, standalone deployment, and custom image building.

## GPU Acceleration

For enhanced performance, you can use GPU acceleration for the Audio2Face service.

### Prerequisites

- Operating system with properly configured NVIDIA Container Toolkit
- NVIDIA GPU hardware supporting CUDA 12

### Starting GPU-Accelerated Services

```bash
# Start all backend services with GPU acceleration
docker compose -f docker-compose-gpu.yml up
```

This will launch the same DLP3D backend infrastructure but with GPU-accelerated Audio2Face service for improved facial animation generation performance.

## Network Proxy Configuration

If you're facing network connectivity issues with upstream services like OpenAI due to network environment restrictions, you can configure a proxy for the orchestrator service.

### Setting Up Proxy

Add the `PROXY_URL` environment variable to the orchestrator container in your `docker-compose.yml` or `docker-compose-gpu.yml` file:

```yaml
services:
  orchestrator:
    environment:
      - PROXY_URL=http://127.0.0.1:7890
    # ... other configuration
```

## Standalone Web Backend Service

To run only the Web Backend service using Docker, you need a pre-configured MongoDB server running separately.

### Quick Start

**Windows:**
```cmd
# Run the Web Backend service only
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dlp3d/web_backend:latest
```

### Command Parameters

| Parameter | Description |
|-----------|-------------|
| `-p 18080:18080` | Maps the container's port 18080 to your host machine's port 18080 |
| `-v .\data:/workspace/web-backend/data` | Mounts your local `data` directory to the container's data directory |
| `-e MONGODB_HOST=your_mongodb_host` | Sets the MongoDB server hostname |
| `-e MONGODB_PORT=27017` | Sets the MongoDB server port (default: 27017) |
| `-e MONGODB_ADMIN_USERNAME=admin` | Sets the MongoDB admin username |
| `-e MONGODB_ADMIN_PASSWORD=your_admin_password` | Sets the MongoDB admin password |
| `dlp3d/web_backend:latest` | Uses the pre-built public image |

### Prerequisites

- Ensure you have a `data` directory in your project root with motion database files
- Make sure Docker is installed and running on your system
- **MongoDB server must be already running and accessible** with the provided connection parameters
- The backend service will automatically create necessary databases in the existing MongoDB server

## Building from Source

If you prefer to build the image from source instead of using the pre-built image:

### Build Process

```cmd
# Build the Docker image
docker build -t web-backend:local .

# Run the container
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password web-backend:local
```

### Build Options

| Option | Description |
|--------|-------------|
| `-t web-backend:local` | Tags the built image with a custom name |
| `--no-cache` | Builds without using cache (useful for clean builds) |
| `--build-arg` | Pass build arguments to the Dockerfile |

---

*For basic Docker usage, see the [main documentation](../README.md).*
