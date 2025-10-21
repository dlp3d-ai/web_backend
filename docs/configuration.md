
# Configuration Guide

## Table of Contents

- [Overview](#overview)
- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Connection Flow](#connection-flow)
- [Usage Examples](#usage-examples)

## Overview

The DLP3D Web Backend uses a flexible configuration system that supports multiple environments and deployment scenarios. This guide covers all configuration options available for the service.

## Configuration Files

The system supports multiple configuration files for different environments:

| File | Purpose | Environment |
|------|---------|-------------|
| `configs/local.py` | Local development configuration | Development |
| `configs/docker.py` | Docker deployment configuration | Containerized |
| `configs/diamond.py` | Production environment configuration | Production |

### Configuration File Structure

Each configuration file contains settings for:
- Database connections
- Service ports and hosts
- Logging levels
- Cache settings
- Security configurations

## Environment Variables

The following environment variables can be used to configure the DLP3D Web Backend service, especially important for Docker deployments:

### Application Database Connection

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `MONGODB_HOST` | MongoDB server hostname | `mongodb` |
| `MONGODB_PORT` | MongoDB server port | `27017` |
| `MONGODB_DATABASE` | Application database name | `web_database` |
| `MONGODB_AUTH_DATABASE` | Authentication database name | `web_database` |
| `MONGODB_USERNAME` | Application username for database access | `web_user` |
| `MONGODB_PASSWORD` | Application password for database access | `web_password` |

### Database Bootstrap (Admin Access)

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `MONGODB_ADMIN_USERNAME` | MongoDB admin username for database bootstrap | `admin` |
| `MONGODB_ADMIN_PASSWORD` | MongoDB admin password for database bootstrap | *(empty)* |

## Connection Flow

The service follows a two-stage connection process to ensure robust database connectivity:

### Stage 1: Primary Connection Attempt

The service first attempts to connect using the application credentials:
- **Username**: `MONGODB_USERNAME`
- **Password**: `MONGODB_PASSWORD`
- **Database**: `MONGODB_DATABASE`

### Stage 2: Bootstrap on Failure

If the primary connection fails (indicating first-time setup), the service automatically uses admin credentials to:

1. **Create Application Database**: Creates the target database if it doesn't exist
2. **Create Application User**: Creates a user with `readWrite` permissions on the target database
3. **Set Up Database Structure**: Initializes necessary collections and indexes

### Stage 3: Retry with Application Credentials

After successful bootstrap, the service retries the connection using application credentials.

## Usage Examples

### Basic Configuration

```bash
# Using default configuration
python main.py

# Using specific configuration file
python main.py --config_path configs/local.py
```

### Docker Environment Variables

```bash
# Set environment variables for Docker deployment
export MONGODB_HOST=your_mongodb_host
export MONGODB_PORT=27017
export MONGODB_ADMIN_USERNAME=admin
export MONGODB_ADMIN_PASSWORD=your_admin_password

# Run with Docker
docker run -e MONGODB_HOST=your_mongodb_host \
           -e MONGODB_ADMIN_PASSWORD=your_admin_password \
           dlp3d/web_backend:latest
```

### Production Configuration

```bash
# Production deployment with secure credentials
export MONGODB_HOST=mongodb_hostname.namespace
export MONGODB_PORT=27017
export MONGODB_DATABASE=dlp3d_web_database
export MONGODB_USERNAME=dlp3d_web_user
export MONGODB_PASSWORD=secure_production_password
export MONGODB_ADMIN_USERNAME=admin
export MONGODB_ADMIN_PASSWORD=secure_admin_password
```

## Best Practices

### Security Considerations

- **First-time deployment**: Only admin credentials need to be configured initially
- **Existing deployments**: Only application credentials are required for normal operation
- **Automatic setup**: The service handles database and user creation automatically on first run

### Environment-Specific Tips

- **Development**: Use `configs/local.py` for local development
- **Docker**: Use environment variables for containerized deployments
- **Production**: Use `configs/diamond.py` with secure credentials

---

*For more information, see the [main documentation](../README.md).*
