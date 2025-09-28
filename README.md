# Web Backend

> **English Documentation** | [中文文档](docs/README_CN.md)

## Table of Contents

- [Overview](#overview)
- [Data Preparation](#data-preparation)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

## Overview

DLP3D Web Backend is a web backend service built with FastAPI and MongoDB, designed to provide RESTful APIs for 3D motion data management, user management, character configuration, and motion file access. The service includes comprehensive motion data handling capabilities with support for multiple data sources including filesystem, MinIO object storage, and MySQL/SQLite databases.

The system is specifically designed for DLP3D web application, providing efficient access to motion files, restpose data, mesh files, and metadata through a unified API interface.

### Key Features

- **Multi-Source Data Access**: Support for filesystem, MinIO object storage, MySQL, and SQLite data sources
- **User Management**: Complete user lifecycle management including creation, authentication, and deletion
- **Character Configuration**: Advanced character management with support for TTS, ASR, classification, conversation, reaction, and memory configurations
- **Motion File API**: High-performance motion data access with caching and version control
- **RESTful API**: Comprehensive REST API with OpenAPI/Swagger documentation
- **MongoDB Integration**: Automatic database bootstrap and user provisioning
- **Caching System**: Intelligent local caching with automatic maintenance and version checking
- **Log Management**: Real-time log access and download capabilities
- **Health Monitoring**: Built-in health check endpoints for service monitoring

### System Architecture

The DLP3D Web Backend follows a modular, layered architecture.

**Core Components:**
- **FastAPIServer**: Main HTTP server with CORS support and error handling
- **MotionFileApiV1**: Motion data access API with caching and version control
- **LocalCache**: Intelligent caching system with automatic maintenance
- **Data Readers**: Modular readers for different data sources
- **MongoDB Integration**: Automatic database setup and user provisioning

## Data Preparation

To use DLP3d web backend service, you need to download the offline motion database and set up the required directory structure.

### Download Motion Database

1. **Download the motion data file:**
   - **Google Drive Download:** [motion_data.zip](https://drive.google.com/file/d/112pnjuIuNqADS-fAT6RUIAVPtb3VlWlq/view?usp=drive_link)
   - **Baidu Cloud：** [motion_data.zip](https://pan.baidu.com/s/1YJSuLaoDKKV7JuE0Ws89zA)（Share Code：`g64i`）

2. **Extract and organize the data:**
   - Extract the downloaded file to your project root directory
   - Ensure the following directory structure is created:

```
├─configs
├─data
│   ├─motion_database.db
│   ├─blendshapes_meta
│   ├─joints_meta
│   ├─mesh_glb
│   ├─motion_files
│   ├─restpose_npz
│   └─rigids_meta
├─dlp3d_web_backend
└─docs
```

### Directory Structure Explanation

- `data/`: Directory containing motion-related data files.
  - `motion_database.db`: SQLite database containing motion metadata.
  - `blendshapes_meta/`: Directory for blendshapes metadata files.
  - `joints_meta/`: Directory for joint metadata files.
  - `mesh_glb/`: Directory for 3D mesh files in GLB format.
  - `motion_files/`: Directory containing motion animation files.
  - `restpose_npz/`: Directory for rest pose data in NPZ format.
  - `rigids_meta/`: Directory for rigid body metadata files.
- The `data` directory will be mounted to the Docker container at `/workspace/web-backend/data`

## Quick Start

### Using Docker

The easiest way to get started with web backend is using the pre-built Docker image:

**Linux/macOS:**
```bash
# Pull and run the pre-built image
docker run -it \
  -p 18080:18080 \
  -v $(pwd)/data:/workspace/web-backend/data \
  -e MONGODB_HOST=your_mongodb_host \
  -e MONGODB_PORT=27017 \
  -e MONGODB_ADMIN_USERNAME=admin \
  -e MONGODB_ADMIN_PASSWORD=your_admin_password \
  dockersenseyang/dlp3d_web_backend:latest
```

**Windows:**
```cmd
# Pull and run the pre-built image
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dockersenseyang/dlp3d_web_backend:latest
```

**Command Explanation:**
- `-p 18080:18080`: Maps the container's port 18080 to your host machine's port 18080
- `-v $(pwd)/data:/workspace/web-backend/data` (Linux/macOS): Mounts your local `data` directory to the container's data directory
- `-v .\data:/workspace/web-backend/data` (Windows): Mounts your local `data` directory to the container's data directory
- `-e MONGODB_HOST=your_mongodb_host`: Sets the MongoDB server hostname
- `-e MONGODB_PORT=27017`: Sets the MongoDB server port (default: 27017)
- `-e MONGODB_ADMIN_USERNAME=admin`: Sets the MongoDB admin username
- `-e MONGODB_ADMIN_PASSWORD=your_admin_password`: Sets the MongoDB admin password
- `dockersenseyang/dlp3d_web_backend:latest`: Uses the pre-built public image

**Prerequisites:**
- Ensure you have a `data` directory in your project root
- Make sure Docker is installed and running on your system
- **MongoDB server must be running and accessible** with the provided connection parameters
- The backend service will automatically create necessary databases in the MongoDB server

**Alternative: Build from Source**

If you prefer to build the image from source:

**Linux/macOS:**
```bash
# Build the Docker image
docker build -t web-backend:local .

# Run the container
docker run -it \
  -p 18080:18080 \
  -v $(pwd)/data:/workspace/web-backend/data \
  -e MONGODB_HOST=your_mongodb_host \
  -e MONGODB_PORT=27017 \
  -e MONGODB_ADMIN_USERNAME=admin \
  -e MONGODB_ADMIN_PASSWORD=your_admin_password \
  web-backend:local
```

**Windows:**
```cmd
# Build the Docker image
docker build -t web-backend:local .

# Run the container
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password web-backend:local
```

## Environment Setup

For local development and deployment, please follow the detailed installation guide:

📖 **[Complete Installation Guide](docs/install.md)**

The installation guide provides step-by-step instructions for:
- Setting up Python 3.10+ environment
- Installing Protocol Buffers compiler
- Configuring the development environment
- Installing project dependencies

### Local Development

After completing the environment setup as described in the installation guide, you can start the service locally:

```bash
# Activate the conda environment
conda activate web-backend

# Start the service
python main.py
```

## API Documentation

The DLP3D Web Backend provides comprehensive RESTful APIs for motion data management, user administration, and character configuration. For detailed API documentation, you can:

#### Interactive API Documentation
Once the service is running, visit the interactive API documentation at:
- **Swagger UI**: `http://localhost:18080/docs`
- **ReDoc**: `http://localhost:18080/redoc`

#### Programmatic API Reference
For developers, the complete API implementation and endpoint definitions can be found in:
- **Server Implementation**: `dlp3d_web_backend/service/server.py`
- **Request/Response Models**: `dlp3d_web_backend/service/requests.py` and `dlp3d_web_backend/service/responses.py`

#### API Categories
The API is organized into the following main categories:
- **User Management** - User lifecycle, authentication, and credential management
- **Character Management** - Character creation, configuration, and management
- **Motion Data Access** - Motion files, restpose data, mesh files, and metadata access
- **System Management** - Health checks, logging, and operational utilities

### API Features
- **OpenAPI Documentation**: Interactive API docs available at `/docs`
- **Error Handling**: Standardized error responses with detailed error messages
- **Authentication**: User-based authentication with credential management
- **Caching**: Intelligent caching for motion data with version control
- **Validation**: Comprehensive request/response validation
- **CORS Support**: Configurable Cross-Origin Resource Sharing

## Configuration

The DLP3D Web Backend uses a flexible configuration system that supports multiple environments and deployment scenarios.

### Configuration Files

The system supports multiple configuration files for different environments:

- `configs/local.py` - Local development configuration
- `configs/docker.py` - Docker deployment configuration  
- `configs/diamond.py` - Production environment configuration

### Environment Variables

The following environment variables can be used to configure the DLP3D Web Backend service, especially important for Docker deployments:

#### Application Database Connection
- `MONGODB_HOST` - MongoDB server hostname (default: `mongodb`)
- `MONGODB_PORT` - MongoDB server port (default: `27017`)
- `MONGODB_DATABASE` - Application database name (default: `web_database`)
- `MONGODB_AUTH_DATABASE` - Authentication database name (default: `web_database`)
- `MONGODB_USERNAME` - Application username for database access (default: `web_user`)
- `MONGODB_PASSWORD` - Application password for database access (default: `web_password`)

#### Database Bootstrap (Admin Access)
- `MONGODB_ADMIN_USERNAME` - MongoDB admin username for database bootstrap (default: `admin`)
- `MONGODB_ADMIN_PASSWORD` - MongoDB admin password for database bootstrap (default: empty)

#### Connection Flow
The service follows a two-stage connection process:

1. **Primary Connection Attempt**: The service first attempts to connect using the application credentials (`MONGODB_USERNAME`, `MONGODB_PASSWORD`) to the target database (`MONGODB_DATABASE`)

2. **Bootstrap on Failure**: If the primary connection fails (indicating first-time setup), the service automatically uses admin credentials (`MONGODB_ADMIN_USERNAME`, `MONGODB_ADMIN_PASSWORD`) to:
   - Create the application database if it doesn't exist
   - Create the application user with `readWrite` permissions on the target database
   - Set up the necessary database structure

3. **Retry with Application Credentials**: After successful bootstrap, the service retries the connection using application credentials

#### Usage Notes
- **First-time deployment**: Only admin credentials need to be configured initially
- **Existing deployments**: Only application credentials are required for normal operation
- **Security**: For production deployments, ensure all passwords are set to secure values
- **Automatic setup**: The service handles database and user creation automatically on first run

Example usage:
```bash
python main.py --config_path configs/local.py
```

## Development

### Key Components

#### API Layer (`apis/`)
- **MotionFileApiV1**: High-level API for motion data access with caching
- **Builder Pattern**: Factory for creating API instances with dependency injection

#### Data Structures (`data_structures/`)
- **MotionClip**: Core motion data structure with transformation support
- **CharacterConfig**: Character configuration with TTS, ASR, and conversation settings
- **UserConfig/UserCredential**: User management data models
- **Annotations**: Motion metadata including keywords, loops, and speech patterns

#### I/O Layer (`io/`)
- **Modular Readers**: Separate readers for files, metadata, and motion data
- **Multi-Source Support**: Filesystem, MinIO, MySQL, and SQLite backends
- **Builder Pattern**: Factory-based reader creation with configuration

#### Service Layer (`service/`)
- **FastAPIServer**: Main HTTP server with comprehensive error handling
- **Request/Response Models**: Type-safe API contracts
- **Exception Handling**: Standardized error responses

#### Cache Layer (`cache/`)
- **LocalCache**: Intelligent caching with automatic maintenance
- **Version Control**: Cache invalidation based on data version changes
- **Memory Management**: Configurable cache size and TTL

### Development Guidelines

- **Type Safety**: Full type annotation support with mypy compatibility
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Logging**: Structured logging with configurable levels and outputs
- **Testing**: Unit tests for all major components
- **Documentation**: Comprehensive docstrings and API documentation


### Code Quality

The project maintains high code quality with:

- **Linting**: Ruff for code style and quality checks
- **Type Hints**: Full type annotation support
- **CI/CD**: Automated testing and deployment pipelines

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

The MIT License is a permissive free software license that allows you to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software with minimal restrictions. The only requirement is that the original copyright notice and license text must be included in all copies or substantial portions of the software.

---
