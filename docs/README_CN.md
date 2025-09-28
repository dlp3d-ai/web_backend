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

1. **下载动作数据文件：**
   - **Google Drive 下载：** [motion_data.zip](https://drive.google.com/file/d/112pnjuIuNqADS-fAT6RUIAVPtb3VlWlq/view?usp=drive_link)
   - **百度网盘：** [motion_data.zip](https://pan.baidu.com/s/1YJSuLaoDKKV7JuE0Ws89zA)（提取码：`g64i`）

2. **解压并整理数据：**
   - 将下载的文件解压到项目根目录
   - 确保创建以下目录结构：

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

### 目录结构说明

- `data/`：包含动作相关数据文件的目录。
  - `motion_database.db`：包含动作数据标注的 SQLite 数据库。
  - `blendshapes_meta/`：用于 blendshapes 元数据文件的目录。
  - `joints_meta/`：用于关节元数据文件的目录。
  - `mesh_glb/`：用于 GLB 格式 3D 网格文件的目录。
  - `motion_files/`：包含动作动画文件的目录。
  - `restpose_npz/`：用于 NPZ 格式静止姿态数据的目录。
  - `rigids_meta/`：用于刚体元数据文件的目录。
- `data` 目录将挂载到 Docker 容器的 `/workspace/web-backend/data`

## 快速开始

### 使用 Docker

使用预构建的 Docker 镜像是开始使用 Web 后端的最简单方法：

**Linux/macOS：**
```bash
# 拉取并运行预构建镜像
docker run -it \
  -p 18080:18080 \
  -v $(pwd)/data:/workspace/web-backend/data \
  -e MONGODB_HOST=your_mongodb_host \
  -e MONGODB_PORT=27017 \
  -e MONGODB_ADMIN_USERNAME=admin \
  -e MONGODB_ADMIN_PASSWORD=your_admin_password \
  dockersenseyang/dlp3d_web_backend:latest
```

**Windows：**
```cmd
# 拉取并运行预构建镜像
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dockersenseyang/dlp3d_web_backend:latest
```

**命令说明：**
- `-p 18080:18080`：将容器的端口 18080 映射到主机端口 18080
- `-v $(pwd)/data:/workspace/web-backend/data`（Linux/macOS）：将本地 `data` 目录挂载到容器的数据目录
- `-v .\data:/workspace/web-backend/data`（Windows）：将本地 `data` 目录挂载到容器的数据目录
- `-e MONGODB_HOST=your_mongodb_host`：设置 MongoDB 服务器主机名
- `-e MONGODB_PORT=27017`：设置 MongoDB 服务器端口（默认：27017）
- `-e MONGODB_ADMIN_USERNAME=admin`：设置 MongoDB 管理员用户名
- `-e MONGODB_ADMIN_PASSWORD=your_admin_password`：设置 MongoDB 管理员密码
- `dockersenseyang/dlp3d_web_backend:latest`：使用预构建的公共镜像

**前置条件：**
- 确保项目根目录中有 `data` 目录
- 确保系统已安装并运行 Docker
- **MongoDB 服务器必须正在运行并可访问**，使用提供的连接参数
- 后端服务将自动在 MongoDB 服务器中创建必要的数据库

**替代方案：从源码构建**

如果您希望从源码构建镜像：

**Linux/macOS：**
```bash
# 构建 Docker 镜像
docker build -t web-backend:local .

# 运行容器
docker run -it \
  -p 18080:18080 \
  -v $(pwd)/data:/workspace/web-backend/data \
  -e MONGODB_HOST=your_mongodb_host \
  -e MONGODB_PORT=27017 \
  -e MONGODB_ADMIN_USERNAME=admin \
  -e MONGODB_ADMIN_PASSWORD=your_admin_password \
  web-backend:local
```

**Windows：**
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

DLP3D Web Backend 使用灵活的配置系统，支持多种环境和部署场景。

### 配置文件

系统支持不同环境的多个配置文件：

- `configs/local.py` - 本地开发配置
- `configs/docker.py` - Docker 部署配置
- `configs/diamond.py` - 生产环境配置

### 环境变量

以下环境变量可用于配置 DLP3D Web Backend 服务，对于 Docker 部署特别重要：

#### 应用程序数据库连接
- `MONGODB_HOST` - MongoDB 服务器主机名（默认：`mongodb`）
- `MONGODB_PORT` - MongoDB 服务器端口（默认：`27017`）
- `MONGODB_DATABASE` - 应用程序数据库名称（默认：`web_database`）
- `MONGODB_AUTH_DATABASE` - 认证数据库名称（默认：`web_database`）
- `MONGODB_USERNAME` - 数据库访问的应用程序用户名（默认：`web_user`）
- `MONGODB_PASSWORD` - 数据库访问的应用程序密码（默认：`web_password`）

#### 数据库引导（管理员访问）
- `MONGODB_ADMIN_USERNAME` - 数据库引导的 MongoDB 管理员用户名（默认：`admin`）
- `MONGODB_ADMIN_PASSWORD` - 数据库引导的 MongoDB 管理员密码（默认：空）

#### 连接流程
服务遵循两阶段连接过程：

1. **主要连接尝试**：服务首先尝试使用应用程序凭据（`MONGODB_USERNAME`、`MONGODB_PASSWORD`）连接到目标数据库（`MONGODB_DATABASE`）

2. **失败时引导**：如果主要连接失败（表示首次设置），服务自动使用管理员凭据（`MONGODB_ADMIN_USERNAME`、`MONGODB_ADMIN_PASSWORD`）来：
   - 创建应用程序数据库（如果不存在）
   - 创建对目标数据库具有 `readWrite` 权限的应用程序用户
   - 设置必要的数据库结构

3. **使用应用程序凭据重试**：成功引导后，服务使用应用程序凭据重试连接

#### 使用说明
- **首次部署**：最初只需要配置管理员凭据
- **现有部署**：正常运行只需要应用程序凭据
- **安全性**：对于生产部署，确保所有密码都设置为安全值
- **自动设置**：服务在首次运行时自动处理数据库和用户创建

使用示例：
```bash
python main.py --config_path configs/local.py
```

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
