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

## Adding New Characters

To add a new character to the system, follow these steps:

### 1. Character Naming

Choose a unique character name for your character (e.g., `MyCharacter`). This name will be used consistently across all configuration files and file paths.

### 2. Required Files

Prepare the following required files for your character:

- **Restpose File** (`.npz` format): Skeleton rest pose data
  - Example path: `data/restpose_npz/my_character_skeleton.npz`
- **Mesh File** (`.glb` format): 3D model mesh data
  - Example path: `data/mesh_glb/my_character.glb`
- **Blendshapes Meta File** (`.json` format): Facial blendshapes metadata
  - Example path: `data/blendshapes_meta/MyCharacter-default_blendshapes_meta.json`

### 3. Optional Files

The following files are optional and only required if you need physics simulation:

- **Joints Meta File** (`.json` format): Joint metadata for physics simulation
  - Example path: `data/joints_meta/MyCharacter-default_joints_meta.json`
- **Rigids Meta File** (`.json` format): Rigid body metadata for physics simulation
  - Example path: `data/rigids_meta/MyCharacter-default_rigids_meta.json`

### 4. Configuration in `configs/community.py`

Add file path references for your character in the following configuration sections:

#### Restpose Reader Configuration

Add an entry to `restpose_reader_cfg['file_paths']`:

```python
restpose_reader_cfg=dict(
    type="FilesystemFileReader",
    name="restpose_reader",
    root_dir='data',
    file_paths={
        # ... existing entries ...
        'MyCharacter': 'restpose_npz/my_character_skeleton.npz',
    },
    logger_cfg=__logger_cfg__
),
```

#### Mesh Reader Configuration

Add an entry to `mesh_reader_cfg['file_paths']`:

```python
'MyCharacter': 'mesh_glb/my_character.glb',
```

#### Blendshapes Meta Reader Configuration

Add an entry to `blendshapes_meta_reader_cfg['file_paths']`:

```python
'MyCharacter': 'blendshapes_meta/MyCharacter-default_blendshapes_meta.json',
```

#### Optional: Joints and Rigids Meta (if using physics simulation)

If you've prepared joints and rigids meta files, add them similarly to their respective `file_paths` dictionaries:

```python
# In joints_meta_reader_cfg['file_paths']:
'MyCharacter': 'joints_meta/MyCharacter-default_joints_meta.json',

# In rigids_meta_reader_cfg['file_paths']:
'MyCharacter': 'rigids_meta/MyCharacter-default_rigids_meta.json',
```

### 5. Character Configuration File

Create a character configuration JSON file following the structure of `configs/community_character_samples_en/keqing-default.json`. Place it in the appropriate directory (e.g., `configs/community_character_samples_en/` or `configs/community_character_samples_zh/`).

Key configuration fields:

- **`character_name`**: Display name for the character (e.g., `"MyCharacter-default"`)
- **`avatar`**: Must match the character name used in `community.py` file paths (e.g., `"MyCharacter"`)
- **`prompt`**: Custom character personality and behavior prompt text
- **`tts_adapter`**: Text-to-speech service provider name (e.g., `"elevenlabs"`, `"zoetrope"`)
- **`voice`**: Voice ID or name from the TTS provider
- **`asr_adapter`**: Automatic speech recognition service provider name
- **`classification_adapter`**: Emotion classification service provider name
- **`conversation_adapter`**: Conversation/LLM service provider name
- **`reaction_adapter`**: Reaction service provider name
- **`memory_adapter`**: Memory service provider name

Example structure:

```json
{
    "character_name": "MyCharacter-default",
    "scene_name": "vast",
    "avatar": "MyCharacter",
    "tts_adapter": "elevenlabs",
    "voice": "your_voice_id",
    "voice_speed": 1.0,
    "asr_adapter": "openai_realtime",
    "classification_adapter": "openai_classification",
    "classification_model_override": "",
    "conversation_adapter": "openai_agent",
    "conversation_model_override": "",
    "prompt": "Your custom character personality prompt here...",
    "reaction_adapter": "openai_reaction",
    "reaction_model_override": "",
    "memory_adapter": "sensenovaomni_memory",
    "memory_model_override": ""
}
```

### 6. Register Character Configuration

Add the path to your character configuration file in `default_character_config_paths` in `configs/community.py`:

```python
default_character_config_paths = [
    # ... existing paths ...
    'configs/community_character_samples_en/my-character-default.json',
]
```

### 7. Grant Character Access to Existing Users

After adding a new character, you need to grant access to existing registered users so they can use the new character. The repository provides a database update tool `tools/update_default_characters.py` for this purpose.

#### Prepare Character List File

Create a JSON file containing the list of default character configuration paths that you want to grant to users. For example, save the following content as `default_characters.json`:

```json
[
    "configs/diamond_character_samples_zh/kq-default.json",
    "configs/diamond_character_samples_zh/fnn-default.json",
    "configs/community_character_samples_en/keqing-default.json",
    "configs/community_character_samples_en/my-character-default.json"
]
```

#### Update Characters in Development Environment

In your development environment, ensure that the required MongoDB environment variables are set, then run:

```bash
python tools/update_default_characters.py --default-character-config-paths default_characters.json
```

If you want to update characters for a specific user, add the `--user-id` parameter:

```bash
python tools/update_default_characters.py \
  --default-character-config-paths default_characters.json \
  --user-id "your_user_id"
```

If `--user-id` is not specified, the tool will prompt you to confirm updating all users in the database.

#### Update Characters in Docker Environment

In a Docker Compose environment, run the tool inside the `web_backend` container:

```bash
docker compose exec web_backend python tools/update_default_characters.py \
  --default-character-config-paths default_characters.json
```

For a specific user:

```bash
docker compose exec web_backend python tools/update_default_characters.py \
  --default-character-config-paths default_characters.json \
  --user-id "your_user_id"
```

**Note**: Ensure that the `default_characters.json` file is accessible within the container. If needed, you can copy the file into the container or place it in a mounted volume.

After the tool completes successfully, all registered users (or the specified user) will have access to the new characters.

---

