# Web Backend

> [English Documentation](README.md) | **中文文档**

## 目录

- [概述](#概述)
- [数据准备](#数据准备)
- [快速开始](#快速开始)
- [许可证](#许可证)

---

📖 **完整文档**：有关安装指南、API 文档、配置选项和开发指南的完整文档，请访问 [DLP3D Web Backend 文档](https://dlp3d.readthedocs.io/zh-cn/latest/_subrepos/web_backend/overview.html)

---

## 概述

DLP3D Web Backend 是一个基于 FastAPI 和 MongoDB 构建的 Web 后端服务，旨在为 3D 动作数据管理、用户管理、角色配置和动作文件访问提供 RESTful API。该服务包含全面的动作数据处理能力，支持多种数据源，包括文件系统、MinIO 对象存储和 MySQL/SQLite 数据库。

该系统专门为 DLP3D Web 应用程序设计，通过统一的 API 接口提供对动作文件、静止姿态数据、模型文件和元数据的高效访问。

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

有关下载链接、目录结构和详细设置说明，请参阅：

📖 **[数据准备文档](https://dlp3d.readthedocs.io/zh-cn/latest/_subrepos/web_backend/data_preparation.html)**

# 快速开始

本指南帮助您使用 Docker 快速运行网页后端服务。对于生产环境或完整的后端服务组，请考虑使用完整的 Docker Compose 方法。

## 使用 Docker

### 推荐：使用 Docker Compose 完整服务

为了获得最佳体验，我们推荐使用 Docker Compose 启动完整的 DLP3D 服务，其中包括网页前后端，以及所有必需的依赖项（MongoDB、Audio2Face、Speech2Motion 等）。

请按照 [ReadTheDocs 上的快速开始指南](https://dlp3d.readthedocs.io/zh-cn/latest/getting_started/quick_start.html) 设置并运行整个基础设施。

### 独立后端服务

如果您只需要独立运行 Web 后端服务（无需完整的 DLP3D 基础设施），可以使用 Docker 或 Docker Compose 进行设置。

有关运行独立后端服务的详细说明，包括 Docker 设置、配置选项和部署指南，请参阅：

📖 **[独立后端服务文档](https://dlp3d.readthedocs.io/zh-cn/latest/_subrepos/web_backend/docker.html)**

文档涵盖：
- Docker 容器设置和配置
- 环境变量和配置选项
- 数据库连接设置
- 服务部署最佳实践


## 许可证

本项目采用 MIT 许可证。详情请参见 [LICENSE](LICENSE) 文件。

MIT 许可证是一个宽松的自由软件许可证，允许您使用、复制、修改、合并、发布、分发、再许可和/或销售软件副本，限制很少。唯一的要求是在所有副本或软件的重要部分中必须包含原始版权声明和许可证文本。

---
