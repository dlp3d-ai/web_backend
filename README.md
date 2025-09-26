# Web Backend Server (FastAPI + MongoDB)

A production-ready web backend service built with FastAPI and MongoDB. It provides RESTful APIs for user management, character configuration, user API key management, log access, and health checks. The service also includes first-run MongoDB bootstrap logic to create the application database and user automatically when needed.

## Table of Contents
- [Features](mdc:#features)
- [Architecture](mdc:#architecture)
- [Installation](mdc:#installation)
- [Configuration](mdc:#configuration)
- [API Overview](mdc:#api-overview)
- [Environment Variables](mdc:#environment-variables)
- [Logs](mdc:#logs)
- [Contributing](mdc:#contributing)
- [Troubleshooting](mdc:#troubleshooting)
- [License](mdc:#license)

## Features
- User lifecycle: create, list, delete
- Character management: list, duplicate, delete
- Character configuration updates:
  - Prompt, ASR, TTS, Classification, Conversation, Reaction, Memory, Scene
- User API key updates and available LLM detection
- Operational utilities: tail/download logs, health endpoint
- OpenAPI/Swagger docs with error schemas (404/503) and response models
- MongoDB bootstrap on startup (database + application user provisioning)

## Architecture
- Language: Python 3.10
- Web Framework: FastAPI
- Database: MongoDB
- Container: Docker (Miniconda-based image)
- Entrypoint: `main.py`
  - `test_mongodb`: checks connectivity and read/write permissions for the app user
  - `setup_mongodb`: creates the database and user if needed
  - Starts `FastAPIServer`

## Installation

### Option A: Docker (recommended)
```bash
# Build image
docker build -t web-backend:latest .

# Run container (override envs as needed)
docker run --rm \
  -e MONGODB_ADMIN_USERNAME=admin \
  -e MONGODB_ADMIN_PASSWORD=your_admin_password \
  -p 80:80 \
  web-backend:latest
```

### Option B: Local (Conda or venv)
```bash
# Using conda (Python 3.10)
conda create -n web python=3.10 -y
conda activate web

# Install
pip install -e .

# Run
python main.py --config_path configs/local.py
```

## Configuration
- Main configuration is provided via a Python module (e.g., `configs/local.py`), loaded by `main.py`.
- Typical keys include (non-exhaustive):
  - `mongodb_host`, `mongodb_port`, `mongodb_database`, `mongodb_auth_database`
  - `mongodb_username`, `mongodb_password`
  - `mongodb_user_collection`, `mongodb_character_collection`
  - `default_user_config_path`, `default_character_config_paths`
  - `host`, `port`, `enable_cors`, `logger_cfg`

Example run:
```bash
python main.py --config_path configs/local.py
```

On startup, the app will:
1. Test connecting to MongoDB using app credentials. If read/write works on the target DB, it continues.
2. If the test fails, it uses admin credentials (from env) to create the database and the application user with `readWrite` role.

## API Overview
Key endpoints (see `/docs` for full schemas):

- GET `/api/v1/list_users` → `ListUsersResponse`
- POST `/api/v1/create_user` → `CreateUserResponse`
- POST `/api/v1/delete_user` → 200 or 404
- GET `/api/v1/list_characters/{user_id}` → `GetCharacterListResponse`
- GET `/api/v1/get_character_config/{user_id}/{character_id}` → 200 or 404
- POST `/api/v1/duplicate_character` → `DuplicateCharacterResponse` (200) or 404
- POST `/api/v1/delete_character` → 200 or 404
- POST `/api/v1/update_character_scene` → 200 or 404
- POST `/api/v1/update_character_prompt|asr|tts|classification|conversation|reaction|memory` → 200 or 404
- POST `/api/v1/update_user_config` → 200
- GET `/api/v1/get_available_llm/{user_id}` → `GetAvailableLLMResponse`
- GET `/tail_log/{n_lines}` → 200 or 503
- GET `/dowload_log_file` → 200 or 503
- GET `/health` → 200 "OK"

Error responses use standardized models hooked via custom exception handlers. OpenAPI docs include 404/503 responses where applicable.

## Environment Variables
These are read by `main.py` to bootstrap MongoDB if needed:

- `MONGODB_ADMIN_USERNAME` (default: `admin`)
- `MONGODB_ADMIN_PASSWORD` (default: empty)

You can export them locally or pass via Docker:
```bash
export MONGODB_ADMIN_USERNAME=admin
export MONGODB_ADMIN_PASSWORD=strong_password
python main.py --config_path configs/local.py
```

## Logs
- Log files are written under the `logs/` directory by default (ensure directory exists).
- Runtime endpoints:
  - Tail logs in-browser: `GET /tail_log/{n_lines}`
  - Download log file: `GET /dowload_log_file`

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Make your changes and ensure code quality:
   ```bash
   # Install ruff if not already installed
   pip install ruff
   
   # Check code style and formatting
   ruff check .
   
   # Auto-fix issues where possible
   ruff check --fix .
   
   # Format code
   ruff format .
   ```
4. Commit your changes with clear messages.
5. Push to your fork and open a Pull Request.

**Note**: Please ensure your code passes `ruff check` before submitting a Pull Request. The CI pipeline will also run these checks.


## Troubleshooting
- Cannot connect to MongoDB:
  - Verify `mongodb_host`, `mongodb_port`, and that MongoDB is reachable.
  - Ensure `MONGODB_ADMIN_USERNAME` and `MONGODB_ADMIN_PASSWORD` are correct when bootstrap is required.
- Auth fails for app user:
  - Check `mongodb_username`/`mongodb_password` in your config.
  - Confirm the user exists in `mongodb_auth_database` with `readWrite` on `mongodb_database`.
- Empty Swagger docs:
  - Confirm the application started without exceptions and visit `/docs`.

## License
Specify your license here (e.g., MIT). If you add a LICENSE file, link it here: `[LICENSE](mdc:LICENSE)`.
