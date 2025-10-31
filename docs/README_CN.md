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

### 整理数据

**解压动作数据库：**
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

# 快速开始

本指南帮助您使用 Docker 快速运行网页后端服务。对于生产环境或完整的后端服务组，请考虑使用完整的 Docker Compose 方法。

## 使用 Docker

### 推荐：使用 Docker Compose 完整服务

为了获得最佳体验，我们推荐使用 Docker Compose 启动完整的 DLP3D 服务，其中包括网页前后端，以及所有必需的依赖项（MongoDB、Audio2Face、Speech2Motion 等）。

请按照 [ReadTheDocs 上的快速开始指南](https://dlp3d.readthedocs.io/en/latest/getting_started/quick_start.html) 设置并运行整个基础设施。

### 独立后端服务

如果您只需要独立运行 Web 后端服务（无需完整的 DLP3D 基础设施），可以使用 Docker 或 Docker Compose 进行设置。

有关运行独立后端服务的详细说明，包括 Docker 设置、配置选项和部署指南，请参阅：

📖 **[独立后端服务文档](https://dlp3d.readthedocs.io/en/latest/_subrepos/web_backend/docker.html)**

文档涵盖：
- Docker 容器设置和配置
- 环境变量和配置选项
- 数据库连接设置
- 服务部署最佳实践


## 环境配置

对于本地开发和部署，请按照详细的安装指南操作：

📖 **[完整安装指南](docs/install.md)**

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

📖 **详细配置指南**：如需了解全面的配置文档，包括环境变量、连接流程和使用示例，请参阅 [配置指南](docs/configuration.md)。

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

本项目采用 MIT 许可证。详情请参见 [LICENSE](LICENSE) 文件。

MIT 许可证是一个宽松的自由软件许可证，允许您使用、复制、修改、合并、发布、分发、再许可和/或销售软件副本，限制很少。唯一的要求是在所有副本或软件的重要部分中必须包含原始版权声明和许可证文本。

---
