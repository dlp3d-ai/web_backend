# Docker 部署指南

## 目录

- [概述](#overview)
- [独立 Web 后端服务](#standalone-service)
- [从源码构建](#build-from-source)

(overview)=
## 概述

本指南介绍 DLP3D Web Backend 服务的 Docker 部署选项，包括独立部署和自定义镜像构建。

(standalone-service)=
## 独立 Web 后端服务

要仅使用 Docker 运行 Web 后端服务，您需要单独运行一个预配置的 MongoDB 服务器。

### 快速开始

**Linux/macOS:**
```bash
# 仅运行 Web 后端服务
docker run -it -p 18080:18080 -v ./data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dlp3d/web_backend:latest
```

**Windows (PowerShell):**
```powershell
# 仅运行 Web 后端服务
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password dlp3d/web_backend:latest
```

### 命令参数

| 参数 | 描述 |
|-----------|-------------|
| `-p 18080:18080` | 将容器的 18080 端口映射到主机的 18080 端口 |
| `-v .\data:/workspace/web-backend/data` | 将本地 `data` 目录挂载到容器的数据目录 |
| `-e MONGODB_HOST=your_mongodb_host` | 设置 MongoDB 服务器主机名 |
| `-e MONGODB_PORT=27017` | 设置 MongoDB 服务器端口（默认：27017） |
| `-e MONGODB_ADMIN_USERNAME=admin` | 设置 MongoDB 管理员用户名 |
| `-e MONGODB_ADMIN_PASSWORD=your_admin_password` | 设置 MongoDB 管理员密码 |
| `dlp3d/web_backend:latest` | 使用预构建的公共镜像 |

### 前置要求

- 确保项目根目录中有包含动作数据库文件的 `data` 目录
- 确保 Docker 已安装并在系统上运行
- **MongoDB 服务器必须已经运行并可访问**，使用提供的连接参数
- 后端服务将在现有的 MongoDB 服务器中自动创建必要的数据库

(build-from-source)=
## 从源码构建

如果您希望从源码构建镜像而不是使用预构建镜像：

### 构建过程

**Linux/macOS:**
```bash
# 构建 Docker 镜像
docker build -t web-backend:local .

# 运行容器
docker run -it -p 18080:18080 -v ./data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password web-backend:local
```

**Windows (PowerShell):**
```powershell
# 构建 Docker 镜像
docker build -t web-backend:local .

# 运行容器
docker run -it -p 18080:18080 -v .\data:/workspace/web-backend/data -e MONGODB_HOST=your_mongodb_host -e MONGODB_PORT=27017 -e MONGODB_ADMIN_USERNAME=admin -e MONGODB_ADMIN_PASSWORD=your_admin_password web-backend:local
```

### 构建选项

| 选项 | 描述 |
|--------|-------------|
| `-t web-backend:local` | 用自定义名称标记构建的镜像 |
| `--no-cache` | 不使用缓存进行构建（适用于全新构建） |
| `--build-arg` | 向 Dockerfile 传递构建参数 |

---
