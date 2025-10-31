# 安装指南

本文档提供了在不同操作系统上设置 DLP3D Web Backend 开发环境的分步说明。

## 目录

- [Linux 环境设置](#linux-setup)
  - [Linux 前置条件](#linux-prerequisites)
  - [Linux 步骤1：安装 Protocol Buffers](#linux-step1-protobuf)
  - [Linux 步骤2：设置 Python](#linux-step2-python)
  - [Linux 步骤3：安装项目](#linux-step3-install)
  - [Linux 步骤4：验证安装](#linux-step4-verify)
  - [Linux 环境激活](#linux-activation)
- [Windows 环境设置](#windows-setup)
  - [Windows 前置条件](#windows-prerequisites)
  - [Windows 步骤1：安装 Protocol Buffers](#windows-step1-protobuf)
  - [Windows 步骤2：设置 Python](#windows-step2-python)
  - [Windows 步骤3：安装项目](#windows-step3-install)
  - [Windows 步骤4：验证安装](#windows-step4-verify)
  - [Windows 环境激活](#windows-activation)
- [MongoDB 安装](#mongodb-installation)
  - [前置条件](#mongodb-prerequisites)
  - [安装说明](#mongodb-instructions)
  - [安装后设置](#mongodb-post-setup)
  - [重要提示](#mongodb-notes)

(linux-setup)=
## Linux 环境设置

(linux-prerequisites)=
### Linux 前置条件

在开始之前，请确保您满足以下系统要求：
- Ubuntu 20.04 或兼容的 Linux 发行版
- 用于下载软件包的网络连接

(linux-step1-protobuf)=
### Linux 步骤1：安装 Protocol Buffers

下载并安装用于 pb 文件编译的 protoc：

```bash
# 创建 protoc 目录
mkdir -p protoc
cd protoc

# 下载 protoc
curl -LjO https://github.com/protocolbuffers/protobuf/releases/download/v31.1/protoc-31.1-linux-x86_64.zip

# 解压并设置权限
unzip protoc-31.1-linux-x86_64.zip
rm -f protoc-31.1-linux-x86_64.zip
chmod +x bin/protoc

# 验证安装
bin/protoc --version

# 返回根目录
cd ..
```

(linux-step2-python)=
### Linux 步骤2：设置 Python

您需要 Python 3.10 或更高版本来运行此项目。本文档提供了使用 conda 安装 Python 的方法作为参考。

**使用 Miniconda 安装 Python：**

```bash
# 下载 Miniconda 安装程序
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 安装 Miniconda
bash Miniconda3-latest-Linux-x86_64.sh

# 清理安装程序
rm -f Miniconda3-latest-Linux-x86_64.sh

# 配置 conda 频道
conda config --add channels conda-forge
conda tos accept

# 使用 Python 3.10 创建 web 环境
conda create -n web python=3.10 -y

# 激活环境
conda activate web

```

(linux-step3-install)=
### Linux 步骤3：安装项目

安装 web backend 包：

```bash
# 确保您在项目根目录
cd /path/to/web_backend

# 激活 conda 环境
conda activate web

# 安装包
pip install .
```

(linux-step4-verify)=
### Linux 步骤4：验证安装

测试一切是否正常工作：

```bash
# 激活环境
conda activate web

# 检查是否可以导入 dlp3d_web_backend.service
python -c "import dlp3d_web_backend.service; print('dlp3d_web_backend.service imported successfully')"

# 检查主应用程序是否运行
python main.py --help
```

(linux-activation)=
### Linux 环境激活

要使用 web backend 项目，请始终首先激活 conda 环境：

```bash
# 激活环境
conda activate web

# 您的终端现在应该显示 (web)
# 您现在可以运行 Python 脚本并使用 dlp3d_web_backend 包
```

(windows-setup)=
## Windows 环境设置

(windows-prerequisites)=
### Windows 前置条件

在开始之前，请确保您满足以下系统要求：
- Windows 10/11 或兼容的 Windows 发行版
- 用于下载软件包的网络连接

(windows-step1-protobuf)=
### Windows 步骤1：安装 Protocol Buffers

下载并安装用于协议缓冲区编译的 protoc：

1. **下载 protoc：**
   - 访问 [Protocol Buffers v31.1 发布页面](https://github.com/protocolbuffers/protobuf/releases/tag/v31.1)
   - 下载 Windows 版本：`protoc-31.1-win64.zip`

2. **解压文件：**
   - 在项目根目录中创建 `protoc` 文件夹
   - 将下载的 `protoc-31.1-win64.zip` 文件解压到 `protoc` 文件夹中
   - 确保可执行文件位于：`protoc\bin\protoc.exe`

3. **验证安装：**
   ```bash
   # 在项目目录中打开命令提示符
   protoc\bin\protoc.exe --version
   ```

(windows-step2-python)=
### Windows 步骤2：设置 Python

您需要 Python 3.10 或更高版本来运行此项目。本文档提供了使用 conda 安装 Python 的方法作为参考。

**使用 Miniconda 安装 Python：**

1. **下载并安装 Miniconda：**
   - 访问 [Miniconda 安装指南](https://www.anaconda.com/docs/getting-started/miniconda/install)
   - 从 Anaconda 网站下载 Windows 安装程序
   - 按照官方安装说明安装 Miniconda
   - **重要**：在安装过程中，确保选中"将 Miniconda3 添加到我的 PATH 环境变量"或在 PATH 环境变量中手动添加 Miniconda3/Scripts 目录，以便从任何终端使用 conda 命令

2. **创建并激活环境：**
   ```bash
   # 使用 Python 3.10 创建 web 环境
   conda create -n web python=3.10 -y
   
   # 激活环境
   conda activate web
   ```

(windows-step3-install)=
### Windows 步骤3：安装项目

安装 web backend 包：

```bash
# 确保您在项目根目录
cd /path/to/web_backend

# 激活 conda 环境
conda activate web

# 临时将 protoc 添加到此会话的 PATH
set PATH=%PATH%;%CD%\protoc\bin

# 安装包
pip install .
```

(windows-step4-verify)=
### Windows 步骤4：验证安装

测试一切是否正常工作：

```bash
# 激活环境
conda activate web

# 检查是否可以导入 dlp3d_web_backend.service
python -c "import dlp3d_web_backend.service; print('dlp3d_web_backend.service imported successfully')"

# 检查主应用程序是否运行
python main.py --help
```

(windows-activation)=
### Windows 环境激活

要使用 web backend 项目，请始终首先激活 conda 环境：

```bash
# 激活环境
conda activate web

# 您的终端现在应该显示 (web)
# 您现在可以运行 Python 脚本并使用 dlp3d_web_backend 包
```

(mongodb-installation)=
## MongoDB 安装

DLP3D Web Backend 服务依赖 MongoDB 进行数据存储和管理。您需要在运行后端服务之前安装和配置 MongoDB。

(mongodb-prerequisites)=
### 前置条件

- MongoDB Community Edition（推荐用于开发）
- MongoDB 服务器必须在您的系统上运行并可访问

(mongodb-instructions)=
### 安装说明

请按照官方 MongoDB 安装指南针对您的操作系统进行操作：

📖 **[MongoDB Community Edition 安装指南](https://www.mongodb.com/docs/manual/installation/)**

官方指南提供了以下系统的详细安装说明：
- **Linux**：Ubuntu、RHEL/CentOS、Debian、Amazon Linux 和其他发行版
- **Windows**：Windows 10/11 和 Windows Server
- **macOS**：Intel 和 Apple Silicon (ARM64) 架构

(mongodb-post-setup)=
### 安装后设置

安装 MongoDB 后，请确保以下事项：

1. **启动 MongoDB 服务：**
   - **Linux/macOS**：`sudo systemctl start mongod` 或 `brew services start mongodb-community`
   - **Windows**：MongoDB 应作为 Windows 服务自动启动

2. **验证 MongoDB 是否运行：**
   ```bash
   # 连接到 MongoDB shell
   mongosh
   
   # 或使用旧版 mongo 命令
   mongo
   ```

3. **为 DLP3D Web Backend 配置 MongoDB：**
   - 后端服务将在首次运行时自动创建必要的数据库和用户
   - 确保 MongoDB 在默认端口（27017）上可访问，或在环境变量中相应配置

(mongodb-notes)=
### 重要提示

- **数据目录**：MongoDB 将自动创建其数据目录。确保有足够的磁盘空间
- **防火墙**：如果在远程服务器上运行，请确保 MongoDB 端口（默认 27017）可访问
