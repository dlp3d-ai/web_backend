# Data Preparation

To use DLP3d web backend service, you need to download the offline motion database and set up the required directory structure.

## Download Motion Database

**Required for Web Backend Service**

To use the DLP3D Web Backend service, you need to download the motion database:

- **Google Drive Download:** [motion_data.zip](https://drive.google.com/file/d/112pnjuIuNqADS-fAT6RUIAVPtb3VlWlq/view?usp=drive_link)
- **Baidu Cloud：** [motion_data.zip](https://pan.baidu.com/s/1YCisRewRQQdYT-GzCZxu-w?pwd=wwqm)

## Organize the data

**Extract motion database:**
   - Create a `data` directory in your project root if it doesn't exist
   - Extract the downloaded `motion_data.zip` file into the `data` directory
   - Ensure the following directory structure is created:

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

## Directory Structure Explanation

**For Web Backend Service:**
- `data/`: Directory containing motion-related data files.
  - `motion_database.db`: SQLite database containing motion metadata.
  - `blendshapes_meta/`: Directory for blendshapes metadata files.
  - `joints_meta/`: Directory for joint metadata files.
  - `mesh_glb/`: Directory for 3D mesh files in GLB format.
  - `motion_files/`: Directory containing motion animation files.
  - `restpose_npz/`: Directory for rest pose data in NPZ format.
  - `rigids_meta/`: Directory for rigid body metadata files.

---

