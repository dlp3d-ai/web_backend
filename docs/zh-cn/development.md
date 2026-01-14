# 开发指南

## 核心组件

### API 层（`apis/`）
- **MotionFileApiV1**：用于动作数据访问的高级 API，具有缓存功能
- **Builder 模式**：用于创建 API 实例的工厂，具有依赖注入功能

### 数据结构（`data_structures/`）
- **MotionClip**：核心动作数据结构，具有转换支持
- **CharacterConfig**：角色配置，包含 TTS、ASR 和对话设置
- **UserConfig/UserCredential**：用户管理数据模型
- **Annotations**：动作元数据，包括关键词、循环和语音模式

### I/O 层（`io/`）
- **模块化读取器**：用于文件、元数据和动作数据的独立读取器
- **多源支持**：文件系统、MinIO、MySQL 和 SQLite 后端
- **Builder 模式**：基于配置的工厂式读取器创建

### 服务层（`service/`）
- **FastAPIServer**：主 HTTP 服务器，具有全面的错误处理
- **请求/响应模型**：类型安全的 API 合约
- **异常处理**：标准化的错误响应

### 缓存层（`cache/`）
- **LocalCache**：智能缓存，具有自动维护功能
- **版本控制**：基于数据版本变化的缓存失效
- **内存管理**：可配置的缓存大小和 TTL

## 开发指南

- **类型安全**：完整的类型注解支持，兼容 mypy
- **错误处理**：全面的异常处理，具有用户友好的消息
- **日志记录**：结构化日志记录，具有可配置的级别和输出
- **测试**：所有主要组件的单元测试
- **文档**：全面的文档字符串和 API 文档

## 代码质量

项目通过以下方式保持高代码质量：

- **代码检查**：使用 Ruff 进行代码风格和质量检查
- **类型提示**：完整的类型注解支持
- **CI/CD**：自动化测试和部署流水线

## 添加新角色

要向系统添加新角色，请按照以下步骤操作：

### 1. 角色命名

为您的角色选择一个唯一的角色名称（例如 `MyCharacter`）。该名称将在所有配置文件和文件路径中一致使用。

### 2. 必需文件

为您的角色准备以下必需文件：

- **Restpose 文件**（`.npz` 格式）：Restpose骨骼数据
  - 示例路径：`data/restpose_npz/my_character_skeleton.npz`
- **Mesh 文件**（`.glb` 格式）：3D 模型网格数据
  - 示例路径：`data/mesh_glb/my_character.glb`
- **Blendshapes Meta 文件**（`.json` 格式）：面部Blendshapes元数据
  - 示例路径：`data/blendshapes_meta/MyCharacter-default_blendshapes_meta.json`

### 3. 可选文件

以下文件是可选的，仅在需要物理模拟时才需要：

- **Joints Meta 文件**（`.json` 格式）：用于物理模拟的Joints元数据
  - 示例路径：`data/joints_meta/MyCharacter-default_joints_meta.json`
- **Rigids Meta 文件**（`.json` 格式）：用于物理模拟的Rigids元数据
  - 示例路径：`data/rigids_meta/MyCharacter-default_rigids_meta.json`

### 4. 在 `configs/community.py` 中配置

在以下配置部分为您的角色添加文件路径引用：

#### Restpose Reader 配置

在 `restpose_reader_cfg['file_paths']` 中添加条目：

```python
restpose_reader_cfg=dict(
    type="FilesystemFileReader",
    name="restpose_reader",
    root_dir='data',
    file_paths={
        # ... 现有条目 ...
        'MyCharacter': 'restpose_npz/my_character_skeleton.npz',
    },
    logger_cfg=__logger_cfg__
),
```

#### Mesh Reader 配置

在 `mesh_reader_cfg['file_paths']` 中添加条目：

```python
'MyCharacter': 'mesh_glb/my_character.glb',
```

#### Blendshapes Meta Reader 配置

在 `blendshapes_meta_reader_cfg['file_paths']` 中添加条目：

```python
'MyCharacter': 'blendshapes_meta/MyCharacter-default_blendshapes_meta.json',
```

#### 可选：Joints 和 Rigids Meta（如果使用物理模拟）

如果您已准备好 joints 和 rigids meta 文件，请将它们类似地添加到各自的 `file_paths` 字典中：

```python
# 在 joints_meta_reader_cfg['file_paths'] 中：
'MyCharacter': 'joints_meta/MyCharacter-default_joints_meta.json',

# 在 rigids_meta_reader_cfg['file_paths'] 中：
'MyCharacter': 'rigids_meta/MyCharacter-default_rigids_meta.json',
```

### 5. 角色配置文件

参照 `configs/community_character_samples_en/keqing-default.json` 的结构创建角色配置 JSON 文件。将其放置在适当的目录中（例如 `configs/community_character_samples_en/` 或 `configs/community_character_samples_zh/`）。

关键配置字段：

- **`character_name`**：角色的显示名称（例如 `"MyCharacter-default"`）
- **`avatar`**：必须与 `community.py` 文件路径中使用的角色名称匹配（例如 `"MyCharacter"`）
- **`prompt`**：自定义角色人格和行为提示词文本
- **`tts_adapter`**：文本转语音服务提供商名称（例如 `"elevenlabs"`、`"zoetrope"`）
- **`voice`**：TTS 提供商的语音 ID 或名称
- **`asr_adapter`**：自动语音识别服务提供商名称
- **`classification_adapter`**：情感分类服务提供商名称
- **`conversation_adapter`**：对话/LLM 服务提供商名称
- **`reaction_adapter`**：反应服务提供商名称
- **`memory_adapter`**：记忆服务提供商名称

示例结构：

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
    "prompt": "您的自定义角色人格提示词...",
    "reaction_adapter": "openai_reaction",
    "reaction_model_override": "",
    "memory_adapter": "sensenovaomni_memory",
    "memory_model_override": ""
}
```

### 6. 注册角色配置

在 `configs/community.py` 的 `default_character_config_paths` 中添加角色配置文件的路径：

```python
default_character_config_paths = [
    # ... 现有路径 ...
    'configs/community_character_samples_en/my-character-default.json',
]
```

### 7. 为现有用户授予角色访问权限

添加新角色后，您需要为现有注册用户授予访问权限，以便他们可以使用新角色。仓库提供了数据库更新工具 `tools/update_default_characters.py` 用于此目的。

#### 准备角色列表文件

创建一个包含您要授予用户的默认角色配置路径列表的 JSON 文件。例如，将以下内容保存为 `default_characters.json`：

```json
[
    "configs/diamond_character_samples_zh/kq-default.json",
    "configs/diamond_character_samples_zh/fnn-default.json",
    "configs/community_character_samples_en/keqing-default.json",
    "configs/community_character_samples_en/my-character-default.json"
]
```

#### 在开发环境中更新角色

在开发环境中，确保已设置所需的 MongoDB 环境变量，然后运行：

```bash
python tools/update_default_characters.py --default-character-config-paths default_characters.json
```

如果要为特定用户更新角色，请添加 `--user-id` 参数：

```bash
python tools/update_default_characters.py \
  --default-character-config-paths default_characters.json \
  --user-id "your_user_id"
```

如果未指定 `--user-id`，工具将提示您确认是否更新数据库中的所有用户。

#### 在 Docker 环境中更新角色

在 Docker Compose 环境中，在 `web_backend` 容器内运行工具：

```bash
docker compose exec web_backend python tools/update_default_characters.py \
  --default-character-config-paths default_characters.json
```

为特定用户更新：

```bash
docker compose exec web_backend python tools/update_default_characters.py \
  --default-character-config-paths default_characters.json \
  --user-id "your_user_id"
```

**注意**：确保 `default_characters.json` 文件在容器中可访问。如果需要，您可以将文件复制到容器中或将其放置在挂载的卷中。

工具成功完成后，所有注册用户（或指定用户）将可以访问新角色。

---
