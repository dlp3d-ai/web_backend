# 配置指南

## 目录

- [概述](#overview)
- [配置文件](#config-files)
- [环境变量](#environment-variables)
- [连接流程](#connection-flow)
- [使用示例](#usage-examples)

(overview)=
## 概述

DLP3D Web Backend 使用灵活的配置系统，支持多种环境和部署场景。本指南涵盖了该服务所有可用的配置选项。

(config-files)=
## 配置文件

系统支持多个用于不同环境的配置文件：

| 文件 | 用途 | 环境 |
|------|---------|-------------|
| `configs/community.py` | 社区版本的 Docker 部署配置 | 容器化 |
| `configs/diamond.py` | 生产环境配置 | 生产环境 |

### 配置文件结构

每个配置文件包含以下设置：
- 数据库连接
- 服务端口和主机
- 日志级别
- 缓存设置
- 安全配置

(environment-variables)=
## 环境变量

以下环境变量可用于配置 DLP3D Web Backend 服务，对于 Docker 部署尤其重要：

### 应用数据库连接

| 变量 | 描述 | 默认值 |
|----------|-------------|---------------|
| `MONGODB_HOST` | MongoDB 服务器主机名 | `mongodb` |
| `MONGODB_PORT` | MongoDB 服务器端口 | `27017` |
| `MONGODB_DATABASE` | 应用数据库名称 | `web_database` |
| `MONGODB_AUTH_DATABASE` | 认证数据库名称 | `web_database` |
| `MONGODB_USERNAME` | 用于数据库访问的用户名 | `web_user` |
| `MONGODB_PASSWORD` | 用于数据库访问的密码 | `web_password` |

### 数据库引导（管理员访问）

| 变量 | 描述 | 默认值 |
|----------|-------------|---------------|
| `MONGODB_ADMIN_USERNAME` | 用于数据库引导的 MongoDB 管理员用户名 | `admin` |
| `MONGODB_ADMIN_PASSWORD` | 用于数据库引导的 MongoDB 管理员密码 | *(empty)* |

(connection-flow)=
## 连接流程

服务遵循两阶段连接过程以确保强健的数据库连接：

### 阶段 1：主连接尝试

服务首先尝试使用应用凭据进行连接：
- **用户名**：`MONGODB_USERNAME`
- **密码**：`MONGODB_PASSWORD`
- **数据库**：`MONGODB_DATABASE`

### 阶段 2：失败时引导

如果主连接失败（表示首次设置），服务会自动使用管理员凭据执行以下操作：

1. **创建应用数据库**：如果目标数据库不存在则创建
2. **创建应用用户**：创建一个在目标数据库上具有 `readWrite` 权限的用户
3. **设置数据库结构**：初始化必要的集合和索引

### 阶段 3：使用应用凭据重试

引导成功后，服务使用应用凭据重试连接。

(usage-examples)=
## 使用示例

### 基本配置

```bash
# 使用默认配置
python main.py

# 使用特定配置文件
python main.py --config_path configs/community.py
```

### Docker 环境变量

```bash
# 为 Docker 部署设置环境变量
export MONGODB_HOST=your_mongodb_host
export MONGODB_PORT=27017
export MONGODB_ADMIN_USERNAME=admin
export MONGODB_ADMIN_PASSWORD=your_admin_password

# 使用 Docker 运行
docker run -e MONGODB_HOST=your_mongodb_host \
           -e MONGODB_ADMIN_PASSWORD=your_admin_password \
           dlp3d/web_backend:latest
```

### 生产环境配置

```bash
# 使用安全凭据的生产部署
export MONGODB_HOST=mongodb_hostname.namespace
export MONGODB_PORT=27017
export MONGODB_DATABASE=dlp3d_web_database
export MONGODB_USERNAME=dlp3d_web_user
export MONGODB_PASSWORD=secure_production_password
export MONGODB_ADMIN_USERNAME=admin
export MONGODB_ADMIN_PASSWORD=secure_admin_password
```

## 最佳实践

### 安全考虑

- **首次部署**：初始只需配置管理员凭据
- **现有部署**：正常操作只需要应用凭据
- **自动设置**：服务在首次运行时会自动处理数据库和用户创建

---
