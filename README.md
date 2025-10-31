# Web Backend

> **English Documentation** | [中文文档](docs/README_CN.md)

## Table of Contents

- [Overview](#overview)
- [Data Preparation](#data-preparation)
- [Quick Start](#quick-start)
- [License](#license)

---

📖 **Full Documentation**: For comprehensive documentation including installation guides, API documentation, configuration options, and development guidelines, please visit [DLP3D Web Backend Documentation](https://dlp3d.readthedocs.io/en/latest/_subrepos/web_backend/overview.html)

---

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

**Required for Web Backend Service**

To use the DLP3D Web Backend service, you need to download the motion database:

- **Google Drive Download:** [motion_data.zip](https://drive.google.com/file/d/112pnjuIuNqADS-fAT6RUIAVPtb3VlWlq/view?usp=drive_link)
- **Baidu Cloud：** [motion_data.zip](https://pan.baidu.com/s/1YCisRewRQQdYT-GzCZxu-w?pwd=wwqm)

### Organize the data

**Extract motion database:**
   - Create a `data` directory in your project root if it doesn't exist
   - Extract the downloaded `motion_data.zip` file into the `data` directory
   - Ensure the following directory structure is created:

```
├─docker-compose.yml
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

**For Web Backend Service:**
- `data/`: Directory containing motion-related data files.
  - `motion_database.db`: SQLite database containing motion metadata.
  - `blendshapes_meta/`: Directory for blendshapes metadata files.
  - `joints_meta/`: Directory for joint metadata files.
  - `mesh_glb/`: Directory for 3D mesh files in GLB format.
  - `motion_files/`: Directory containing motion animation files.
  - `restpose_npz/`: Directory for rest pose data in NPZ format.
  - `rigids_meta/`: Directory for rigid body metadata files.

# Quick Start

This guide helps you run web backend service quickly using Docker. For production or a full backend stack, consider the complete Docker Compose approach.

## Using Docker

### Recommended: Complete Services with Docker Compose

For the best experience, we recommend using Docker Compose to start the complete DLP3D services, which includes the web backend service and the web frontend service along with all required dependencies (MongoDB, Audio2Face, Speech2Motion, etc.).

Please follow the [Quick Start guide on ReadTheDocs](https://dlp3d.readthedocs.io/en/latest/getting_started/quick_start.html) to set up and run the entire infrastructure.

### Standalone Backend Service

If you only need to run the web backend service independently (without the full DLP3D infrastructure), you can set it up using Docker or Docker Compose.

For detailed instructions on running the standalone backend service, including Docker setup, configuration options, and deployment guidelines, please refer to:

📖 **[Standalone Backend Service Documentation](https://dlp3d.readthedocs.io/en/latest/_subrepos/web_backend/docker.html)**

The documentation covers:
- Docker container setup and configuration
- Environment variables and configuration options
- Database connection setup
- Service deployment best practices



## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

The MIT License is a permissive free software license that allows you to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software with minimal restrictions. The only requirement is that the original copyright notice and license text must be included in all copies or substantial portions of the software.

---
