# Web Backend

> [English Documentation](../README.md) | **中文文档**

## 目录

- [概述](#概述)
- [数据准备](#数据准备)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [API 文档](#api-文档)
- [配置说明](#配置说明)
- [开发指南](#开发指南)
- [许可证](#许可证)

## 概述

DLP3D Web Backend 是一个基于 FastAPI 和 MongoDB 构建的 Web 后端服务，旨在为 3D 动作数据管理、用户管理、角色配置和动作文件访问提供 RESTful API。该服务包含全面的动作数据处理能力，支持多种数据源，包括文件系统、MinIO 对象存储和 MySQL/SQLite 数据库。

该系统专门为 DLP3D Web 应用程序设计，通过统一的 API 接口提供对动作文件、静止姿态数据、网格文件和元数据的高效访问。

### 核心特性

- **多源数据访问**：支持文件系统、MinIO 对象存储、MySQL 和 SQLite 数据源
- **用户管理**：完整的用户生命周期管理，包括创建、认证和删除
- **角色配置**：高级角色管理，支持 TTS、ASR、分类、对话、反应和记忆配置
- **动作文件 API**：高性能动作数据访问，具有缓存和版本控制功能
- **RESTful API**：全面的 REST API，包含 OpenAPI/Swagger 文档
- **MongoDB 集成**：自动数据库引导和用户配置
- **缓存系统**：智能本地缓存，具有自动维护和版本检查功能
- **日志管理**：实时日志访问和下载功能
- **健康监控**：内置健康检查端点，用于服务监控

### 系统架构

DLP3D Web Backend 采用模块化、分层架构。

**核心组件：**
- **FastAPIServer**：主 HTTP 服务器，支持 CORS 和错误处理
- **MotionFileApiV1**：动作数据访问 API，具有缓存和版本控制功能
- **LocalCache**：智能缓存系统，具有自动维护功能
- **Data Readers**：用于不同数据源的模块化读取器
- **MongoDB 集成**：自动数据库设置和用户配置

## 数据准备

要使用 DLP3D Web 后端服务，您需要下载离线动作数据库并设置所需的目录结构。

### 下载动作数据库

**Web Backend 服务必需**

要使用 DLP3D Web Backend 服务，您需要下载动作数据库：

- **Google Drive 下载：** [motion_data.zip](https://drive.google.com/file/d/112pnjuIuNqADS-fAT6RUIAVPtb3VlWlq/view?usp=drive_link)
- **百度网盘：** [motion_data.zip](https://pan.baidu.com/s/1YJSuLaoDKKV7JuE0Ws89zA)（提取码：`g64i`）

### 下载 Audio2Face 模型文件

**完整 DLP3D Web 应用必需**

要实现完整的 DLP3D Web 应用功能，您还需要下载 Audio2Face 模型文件：

- **GitHub 下载：** [unitalker_v0.4.0_base.onnx](https://github.com/LazyBusyYang/CatStream/releases/download/a2f_cicd_files/unitalker_v0.4.0_base.onnx)
- **Google Drive 下载：** [unitalker_v0.4.0_base.onnx](https://drive.google.com/file/d/1E0NTrsh4mciRPb265n64Dd5vR3Sa7Dgx/view?usp=drive_link)
- **百度网盘：** [unitalker_v0.4.0_base.onnx](https://pan.baidu.com/s/1A_vUj_ZBMFPbO1lgUYVCPA)（提取码：`shre`）

> **注意**：Audio2Face 模型仅在运行完整的 DLP3D Web 应用时才需要。对于独立的 Web Backend 服务，只需要动作数据库。

### 整理数据

**Web Backend 服务（必需）：**

1. **解压动作数据库：**
   - 如果项目根目录中不存在 `data` 目录，请创建一个
   - 将下载的 `motion_data.zip` 文件解压到 `data` 目录中
   - 确保创建以下目录结构：

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

**完整 DLP3D Web 应用（可选）：**

2. **整理 Audio2Face 模型：**
   - 如果项目根目录中不存在 `weights` 目录，请创建一个
   - 将下载的 `unitalker_v0.4.0_base.onnx` 文件放置在 `weights` 目录中

```
├─weights
│   └─unitalker_v0.4.0_base.onnx
├─dlp3d_web_backend
└─docs
```

### 目录结构说明

**Web Backend 服务：**
- `data/`：包含动作相关数据文件的目录。
  - `motion_database.db`：包含动作数据标注的 SQLite 数据库。
  - `blendshapes_meta/`：用于 blendshapes 元数据文件的目录。
  - `joints_meta/`：用于关节元数据文件的目录。
  - `mesh_glb/`：用于 GLB 格式 3D 网格文件的目录。
  - `motion_files/`：包含动作动画文件的目录。
  - `restpose_npz/`：用于 NPZ 格式静止姿态数据的目录。
  - `rigids_meta/`：用于刚体元数据文件的目录。
- `weights/`：用于存储 ONNX 模型文件的目录。
  - `unitalker_v0.4.0_base.onnx`：用于音频转面部生成的主要 ONNX 模型文件。

## 快速开始

### 完整的 DLP3D 后端服务

完成上述数据准备步骤后，您可以使用单个命令启动所有 DLP3D 后端服务：

```bash
# 启动所有后端服务
docker compose up
```

这将启动完整的 DLP3D 后端基础设施，包括：

- **MongoDB 数据库服务** - 数据存储和管理
- **Web Backend 服务** - RESTful API 服务器（端口 18080）
- **Orchestrator 服务** - 流式对话和动画生成（端口 18081）
- **Speech2Motion 服务** - 从语音生成动作动画
- **Audio2Face 服务** - 从音频生成面部动画

**前端连接：**
一旦所有服务运行，您的前端应用程序只需要连接到：
- **Backend API**：`http://localhost:18080`（Web Backend 服务）
- **Orchestrator API**：`http://localhost:18081`（Orchestrator 服务）

📖 **高级 Docker 用法**：如需了解更多详细的 Docker 部署选项，包括 GPU 加速、网络代理配置和故障排除，请参阅 [Docker 部署指南](docker.md)。

#### 使用 GPU 加速 Audio2Face

为了获得更好的性能，您可以为 Audio2Face 服务使用 GPU 加速。这需要：

**前提条件：**
- 操作系统正确配置了 NVIDIA Container Toolkit
- 具有支持 CUDA 12 的 NVIDIA GPU 硬件

**启动 GPU 加速服务：**
```bash
# 启动所有支持 GPU 加速的后端服务
docker compose -f docker-compose-gpu.yml up
```

这将启动相同的 DLP3D 后端基础设施，但 Audio2Face 服务将使用 GPU 加速，以提升面部动画生成的性能。

### 使用 Docker（独立 Web Backend 服务）

要仅使用 Docker 运行 Web Backend 服务，您需要预先配置的 MongoDB 服务器单独运行：

**Windows：**
```cmd
# 仅运行 Web Backend 服务
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dockersenseyang/dlp3d_web_backend:latest
```

**命令说明：**
- `-p 18080:18080`：将容器的端口 18080 映射到主机端口 18080
- `-v .\data:/workspace/web-backend/data`：将本地 `data` 目录挂载到容器的数据目录
- `-e MONGODB_HOST=your_mongodb_host`：设置 MongoDB 服务器主机名
- `-e MONGODB_PORT=27017`：设置 MongoDB 服务器端口（默认：27017）
- `-e MONGODB_ADMIN_USERNAME=admin`：设置 MongoDB 管理员用户名
- `-e MONGODB_ADMIN_PASSWORD=your_admin_password`：设置 MongoDB 管理员密码
- `dockersenseyang/dlp3d_web_backend:latest`：使用预构建的公共镜像

**前置条件：**
- 确保项目根目录中有包含动作数据库文件的 `data` 目录
- 确保系统已安装并运行 Docker
- **MongoDB 服务器必须已经运行并可访问**，使用提供的连接参数
- 后端服务将在现有 MongoDB 服务器中自动创建必要的数据库

**替代方案：从源码构建**

如果您希望从源码构建镜像：

```cmd
# 构建 Docker 镜像
docker build -t web-backend:local .

# 运行容器
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password web-backend:local
```

## 环境配置

对于本地开发和部署，请按照详细的安装指南操作：

📖 **[完整安装指南](install.md)**

安装指南提供以下步骤说明：
- 设置 Python 3.10+ 环境
- 安装 Protocol Buffers 编译器
- 配置开发环境
- 安装项目依赖

### 本地开发

按照安装指南完成环境设置后，您可以在本地启动服务：

```bash
# 激活 conda 环境
conda activate web-backend

# 启动服务
python main.py
```

## API 文档

DLP3D Web Backend 为动作数据管理、用户管理和角色配置提供全面的 RESTful API。要获取详细的 API 文档，您可以：

#### 交互式 API 文档
服务运行后，访问交互式 API 文档：
- **Swagger UI**：`http://localhost:18080/docs`
- **ReDoc**：`http://localhost:18080/redoc`

#### 编程式 API 参考
对于开发者，完整的 API 实现和端点定义可以在以下文件中找到：
- **服务器实现**：`dlp3d_web_backend/service/server.py`
- **请求/响应模型**：`dlp3d_web_backend/service/requests.py` 和 `dlp3d_web_backend/service/responses.py`

#### API 分类
API 按以下主要类别组织：
- **用户管理** - 用户生命周期、认证和凭据管理
- **角色管理** - 角色创建、配置和管理
- **动作数据访问** - 动作文件、静止姿态数据、网格文件和元数据访问
- **系统管理** - 健康检查、日志记录和操作工具

### API 特性
- **OpenAPI 文档**：在 `/docs` 提供交互式 API 文档
- **错误处理**：标准化的错误响应，包含详细的错误消息
- **认证**：基于用户的认证和凭据管理
- **缓存**：动作数据的智能缓存，具有版本控制功能
- **验证**：全面的请求/响应验证
- **CORS 支持**：可配置的跨域资源共享

## 配置说明

DLP3D Web Backend 使用灵活的配置系统，支持多种环境和部署场景。系统支持各种配置文件和环境变量，满足不同的部署需求。

### 配置选项

- **配置文件**：多环境特定配置文件
- **环境变量**：Docker 部署的全面环境变量支持
- **数据库连接**：自动数据库设置和用户配置
- **连接流程**：两阶段连接过程确保数据库连接稳定性

📖 **详细配置指南**：如需了解全面的配置文档，包括环境变量、连接流程和使用示例，请参阅 [配置指南](configuration.md)。

## 开发指南

### 核心组件

#### API 层（`apis/`）
- **MotionFileApiV1**：用于动作数据访问的高级 API，具有缓存功能
- **Builder 模式**：用于创建 API 实例的工厂，具有依赖注入功能

#### 数据结构（`data_structures/`）
- **MotionClip**：核心动作数据结构，具有转换支持
- **CharacterConfig**：角色配置，包含 TTS、ASR 和对话设置
- **UserConfig/UserCredential**：用户管理数据模型
- **Annotations**：动作元数据，包括关键词、循环和语音模式

#### I/O 层（`io/`）
- **模块化读取器**：用于文件、元数据和动作数据的独立读取器
- **多源支持**：文件系统、MinIO、MySQL 和 SQLite 后端
- **Builder 模式**：基于配置的工厂式读取器创建

#### 服务层（`service/`）
- **FastAPIServer**：主 HTTP 服务器，具有全面的错误处理
- **请求/响应模型**：类型安全的 API 合约
- **异常处理**：标准化的错误响应

#### 缓存层（`cache/`）
- **LocalCache**：智能缓存，具有自动维护功能
- **版本控制**：基于数据版本变化的缓存失效
- **内存管理**：可配置的缓存大小和 TTL

### 开发指南

- **类型安全**：完整的类型注解支持，兼容 mypy
- **错误处理**：全面的异常处理，具有用户友好的消息
- **日志记录**：结构化日志记录，具有可配置的级别和输出
- **测试**：所有主要组件的单元测试
- **文档**：全面的文档字符串和 API 文档

### 代码质量

项目通过以下方式保持高代码质量：

- **代码检查**：使用 Ruff 进行代码风格和质量检查
- **类型提示**：完整的类型注解支持
- **CI/CD**：自动化测试和部署管道

## 许可证

本项目采用MIT许可证。详情请参见[LICENSE](LICENSE)文件。

MIT许可证是一个宽松的自由软件许可证，允许您使用、复制、修改、合并、发布、分发、再许可和/或销售软件副本，限制很少。唯一的要求是在所有副本或软件的重要部分中必须包含原始版权声明和许可证文本。
---
