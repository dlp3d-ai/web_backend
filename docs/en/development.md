# Development

## Key Components

### API Layer (`apis/`)
- **MotionFileApiV1**: High-level API for motion data access with caching
- **Builder Pattern**: Factory for creating API instances with dependency injection

### Data Structures (`data_structures/`)
- **MotionClip**: Core motion data structure with transformation support
- **CharacterConfig**: Character configuration with TTS, ASR, and conversation settings
- **UserConfig/UserCredential**: User management data models
- **Annotations**: Motion metadata including keywords, loops, and speech patterns

### I/O Layer (`io/`)
- **Modular Readers**: Separate readers for files, metadata, and motion data
- **Multi-Source Support**: Filesystem, MinIO, MySQL, and SQLite backends
- **Builder Pattern**: Factory-based reader creation with configuration

### Service Layer (`service/`)
- **FastAPIServer**: Main HTTP server with comprehensive error handling
- **Request/Response Models**: Type-safe API contracts
- **Exception Handling**: Standardized error responses

### Cache Layer (`cache/`)
- **LocalCache**: Intelligent caching with automatic maintenance
- **Version Control**: Cache invalidation based on data version changes
- **Memory Management**: Configurable cache size and TTL

## Development Guidelines

- **Type Safety**: Full type annotation support with mypy compatibility
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Logging**: Structured logging with configurable levels and outputs
- **Testing**: Unit tests for all major components
- **Documentation**: Comprehensive docstrings and API documentation


## Code Quality

The project maintains high code quality with:

- **Linting**: Ruff for code style and quality checks
- **Type Hints**: Full type annotation support
- **CI/CD**: Automated testing and deployment pipelines

---

