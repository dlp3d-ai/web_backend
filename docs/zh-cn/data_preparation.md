# 数据准备

要使用 DLP3D Web 后端服务，您需要下载离线动作数据库并设置所需的目录结构。

## 下载动作数据库

**Web Backend 服务必需**

要使用 DLP3D Web Backend 服务，您需要下载动作数据库：

- **Google Drive 下载：** [motion_data.zip](https://drive.google.com/file/d/112pnjuIuNqADS-fAT6RUIAVPtb3VlWlq/view?usp=drive_link)
- **百度网盘：** [motion_data.zip](https://pan.baidu.com/s/1YCisRewRQQdYT-GzCZxu-w?pwd=wwqm)

## 整理数据

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

## 目录结构说明

**Web Backend 服务：**
- `data/`：包含动作相关数据文件的目录。
  - `motion_database.db`：包含动作数据标注的 SQLite 数据库。
  - `blendshapes_meta/`：用于 blendshapes 元数据文件的目录。
  - `joints_meta/`：用于关节元数据文件的目录。
  - `mesh_glb/`：用于 GLB 格式 3D 网格文件的目录。
  - `motion_files/`：包含动作动画文件的目录。
  - `restpose_npz/`：用于 NPZ 格式静止姿态数据的目录。
  - `rigids_meta/`：用于刚体元数据文件的目录。

---

