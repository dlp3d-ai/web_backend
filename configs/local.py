import numpy as np

# CRITICAL = 50
# ERROR = 40
# WARNING = 30
# INFO = 20
# DEBUG = 10
# NOTSET = 0
__logger_cfg__ = dict(
    logger_name="root",
    aws_level=10,
    file_level=10,
    console_level=20,
    logger_path='logs/server.log',
)

type = 'FastAPIServer'
mongodb_host = '127.0.0.1'
mongodb_port = 27017
mongodb_username = 'web_user'
mongodb_password = 'web_password'
mongodb_database = 'web_database'
mongodb_auth_database = 'web_database'
default_character_config_paths = [
    'configs/kq-default_sample.json', 'configs/ani-default_sample.json']
enable_cors = True
host = '0.0.0.0'
port = 18080
logger_cfg = __logger_cfg__

motion_file_api_cfg = dict(
    type="MotionFileApiV1",
    meta_reader_cfg=dict(
        type="SQLiteMetaReader",
        sqlite_path='data/motion_database.db',
        sqlite_join_cmd_path='configs/3dac_sql_join.sql',
        logger_cfg=__logger_cfg__
    ),
    motion_reader_cfg=dict(
        type="SQLiteFilesystemMotionReader",
        sqlite_path='data/motion_database.db',
        sqlite_join_cmd_path='configs/3dac_sql_join.sql',
        root_dir='data/motion_files',
        float_dtype=np.float32,
        logger_cfg=__logger_cfg__
    ),
    restpose_reader_cfg=dict(
        type="FilesystemFileReader",
        name="restpose_reader",
        root_dir='data',
        file_paths={
            'KQ-default': 'restpose_npz/KQ_default_0326_skeleton.npz',
            'FNN-default': 'restpose_npz/FNN_default_0819_skeleton.npz',
            'HT-default': 'restpose_npz/HT_default_0819_skeleton.npz',
            'Ani-default': 'restpose_npz/Ani_default_0827_skeleton.npz'
        },
        logger_cfg=__logger_cfg__
    ),
    mesh_reader_cfg=dict(
        type="FilesystemFileReader",
        name="mesh_reader",
        root_dir='data',
        file_paths={
            'KQ-default': 'mesh_glb/keqing.glb',
            'FNN-default': 'mesh_glb/funingna.glb',
            'HT-default': 'mesh_glb/hutao.glb',
            'Ani-default': 'mesh_glb/ani.glb'
        },
        logger_cfg=__logger_cfg__
    ),
    joints_meta_reader_cfg=dict(
        type="FilesystemFileReader",
        name="joints_meta_reader",
        root_dir='data',
        file_paths={
            'KQ-default': 'joints_meta/KQ-default_joints_meta.json',
            'FNN-default': 'joints_meta/FNN-default_joints_meta.json',
            'HT-default': 'joints_meta/HT-default_joints_meta.json',
            'Ani-default': 'joints_meta/Ani-default_joints_meta.json'
        },
        logger_cfg=__logger_cfg__
    ),
    rigids_meta_reader_cfg=dict(
        type="FilesystemFileReader",
        name="rigids_meta_reader",
        root_dir='data',
        file_paths={
            'KQ-default': 'rigids_meta/KQ-default_rigids_meta.json',
            'FNN-default': 'rigids_meta/FNN-default_rigids_meta.json',
            'HT-default': 'rigids_meta/HT-default_rigids_meta.json',
            'Ani-default': 'rigids_meta/Ani-default_rigids_meta.json'
        },
        logger_cfg=__logger_cfg__
    ),
    blendshapes_meta_reader_cfg=dict(
        type="FilesystemFileReader",
        name="blendshapes_meta_reader",
        root_dir='data',
        file_paths={
            'KQ-default': 'blendshapes_meta/KQ-default_blendshapes_meta.json',
            'Ani-default': 'blendshapes_meta/Ani-default_blendshapes_meta.json'
        },
        logger_cfg=__logger_cfg__
    ),
    cache_cfg=dict(
        type="LocalCache",
        logger_cfg=__logger_cfg__
    ),
    maintain_check_interval=60,
    logger_cfg=__logger_cfg__,
)

