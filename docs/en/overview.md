# Overview

DLP3D Web Backend is a web backend service built with FastAPI and MongoDB, designed to provide RESTful APIs for 3D motion data management, user management, character configuration, and motion file access. The service includes comprehensive motion data handling capabilities with support for multiple data sources including filesystem, MinIO object storage, and MySQL/SQLite databases.

The system is specifically designed for DLP3D web application, providing efficient access to motion files, restpose data, mesh files, and metadata through a unified API interface.

## Key Features

- **Multi-Source Data Access**: Support for filesystem, MinIO object storage, MySQL, and SQLite data sources
- **User Management**: Complete user lifecycle management including creation, authentication, and deletion
- **Character Configuration**: Advanced character management with support for TTS, ASR, classification, conversation, reaction, and memory configurations
- **Motion File API**: High-performance motion data access with caching and version control
- **RESTful API**: Comprehensive REST API with OpenAPI/Swagger documentation
- **MongoDB Integration**: Automatic database bootstrap and user provisioning
- **Caching System**: Intelligent local caching with automatic maintenance and version checking
- **Log Management**: Real-time log access and download capabilities
- **Health Monitoring**: Built-in health check endpoints for service monitoring

## System Architecture

The DLP3D Web Backend follows a modular, layered architecture.

**Core Components:**
- **FastAPIServer**: Main HTTP server with CORS support and error handling
- **MotionFileApiV1**: Motion data access API with caching and version control
- **LocalCache**: Intelligent caching system with automatic maintenance
- **Data Readers**: Modular readers for different data sources
- **MongoDB Integration**: Automatic database setup and user provisioning

---

