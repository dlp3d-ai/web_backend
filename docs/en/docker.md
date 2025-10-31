# Docker Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Standalone Web Backend Service](#standalone-web-backend-service)
- [Building from Source](#building-from-source)

## Overview

This guide covers Docker deployment options for the DLP3D Web Backend service, including standalone deployment and custom image building.

## Standalone Web Backend Service

To run only the Web Backend service using Docker, you need a pre-configured MongoDB server running separately.

### Quick Start

**Linux/macOS:**
```bash
# Run the Web Backend service only
docker run -it -p 18080:18080 -v ./data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dlp3d/web_backend:latest
```

**Windows (PowerShell):**
```powershell
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

**Linux/macOS:**
```bash
# Build the Docker image
docker build -t web-backend:local .

# Run the container
docker run -it -p 18080:18080 -v ./data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password web-backend:local
```

**Windows (PowerShell):**
```powershell
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
