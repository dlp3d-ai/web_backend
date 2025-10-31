# API Documentation

The DLP3D Web Backend provides comprehensive RESTful APIs for motion data management, user administration, and character configuration. For detailed API documentation, you can:

## Interactive API Documentation

Once the service is running, visit the interactive API documentation at:
- **Swagger UI**: `http://localhost:18080/docs`
- **ReDoc**: `http://localhost:18080/redoc`

## Programmatic API Reference

For developers, the complete API implementation and endpoint definitions can be found in:
- **Server Implementation**: `dlp3d_web_backend/service/server.py`
- **Request/Response Models**: `dlp3d_web_backend/service/requests.py` and `dlp3d_web_backend/service/responses.py`

## API Categories

The API is organized into the following main categories:
- **User Management** - User lifecycle, authentication, and credential management
- **Character Management** - Character creation, configuration, and management
- **Motion Data Access** - Motion files, restpose data, mesh files, and metadata access
- **System Management** - Health checks, logging, and operational utilities

## API Features

- **OpenAPI Documentation**: Interactive API docs available at `/docs`
- **Error Handling**: Standardized error responses with detailed error messages
- **Authentication**: User-based authentication with credential management
- **Caching**: Intelligent caching for motion data with version control
- **Validation**: Comprehensive request/response validation
- **CORS Support**: Configurable Cross-Origin Resource Sharing

---

