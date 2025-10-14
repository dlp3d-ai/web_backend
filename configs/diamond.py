import os

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
mongodb_host = os.environ.get('MONGODB_HOST')
mongodb_port = int(os.environ.get('MONGODB_PORT', 27017))
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_database = os.environ.get('MONGODB_DATABASE')
mongodb_auth_database = os.environ.get('MONGODB_AUTH_DATABASE')
default_character_config_paths = [
    'configs/kq-default_community_sample.json',
    'configs/fnn-default_community_sample.json',
    'configs/ht-default_community_sample.json',
    'configs/ani-default_community_sample.json']
default_user_config_path = 'secrets/user_sample.json'
enable_cors = True
host = '0.0.0.0'
port = 8080
logger_cfg = __logger_cfg__

motion_file_api_cfg = dict(
    type="MotionFileApiV1",
    meta_reader_cfg=dict(
        type="MySQLMetaReader",
        mysql_host=os.getenv('MYSQL_HOST'),
        mysql_port=os.getenv('MYSQL_PORT'),
        mysql_username=os.getenv('MYSQL_USER'),
        mysql_password=os.getenv('MYSQL_PASSWORD'),
        mysql_database='motion_db',
        mysql_join_cmd_path='configs/3dac_sql_join.sql',
        logger_cfg=__logger_cfg__
    ),
    motion_reader_cfg=dict(
        type="MinioMySQLMotionReader",
        mysql_host=os.getenv('MYSQL_HOST'),
        mysql_port=os.getenv('MYSQL_PORT'),
        mysql_username=os.getenv('MYSQL_USER'),
        mysql_password=os.getenv('MYSQL_PASSWORD'),
        mysql_database='motion_db',
        mysql_join_cmd_path='configs/3dac_sql_join.sql',
        endpoint=os.getenv('OSS_ENDPOINT'),
        access_key=os.getenv('OSS_ACCESS_KEY'),
        secret_key=os.getenv('OSS_SECRET_KEY'),
        bucket_name='3dac',
        float_dtype=np.float32,
        logger_cfg=__logger_cfg__
    ),
    restpose_reader_cfg=dict(
        type="MinioFileReader",
        name="restpose_reader",
        file_paths={
            'KQ-default': 'restpose_npz/KQ_default_0326_skeleton.npz',
            'FNN-default': 'restpose_npz/FNN_default_0819_skeleton.npz',
            'HT-default': 'restpose_npz/HT_default_0819_skeleton.npz',
            'Ani-default': 'restpose_npz/Ani_default_0827_skeleton.npz'
        },
        endpoint=os.getenv('OSS_ENDPOINT'),
        access_key=os.getenv('OSS_ACCESS_KEY'),
        secret_key=os.getenv('OSS_SECRET_KEY'),
        bucket_name='3dac',
        logger_cfg=__logger_cfg__
    ),
    mesh_reader_cfg=dict(
        type="MinioFileReader",
        name="mesh_reader",
        file_paths={
            'KQ-default': 'mesh_glb/keqing.glb',
            'FNN-default': 'mesh_glb/funingna.glb',
            'HT-default': 'mesh_glb/hutao.glb',
            'Ani-default': 'mesh_glb/ani.glb'
        },
        endpoint=os.getenv('OSS_ENDPOINT'),
        access_key=os.getenv('OSS_ACCESS_KEY'),
        secret_key=os.getenv('OSS_SECRET_KEY'),
        bucket_name='3dac',
        logger_cfg=__logger_cfg__
    ),
    joints_meta_reader_cfg=dict(
        type="MinioFileReader",
        name="joints_meta_reader",
        file_paths={
            'KQ-default': 'joints_meta/KQ-default_joints_meta.json',
            'FNN-default': 'joints_meta/FNN-default_joints_meta.json',
            'HT-default': 'joints_meta/HT-default_joints_meta.json',
            'Ani-default': 'joints_meta/Ani-default_joints_meta.json'
        },
        endpoint=os.getenv('OSS_ENDPOINT'),
        access_key=os.getenv('OSS_ACCESS_KEY'),
        secret_key=os.getenv('OSS_SECRET_KEY'),
        bucket_name='3dac',
        logger_cfg=__logger_cfg__
    ),
    rigids_meta_reader_cfg=dict(
        type="MinioFileReader",
        name="rigids_meta_reader",
        file_paths={
            'KQ-default': 'rigids_meta/KQ-default_rigids_meta.json',
            'FNN-default': 'rigids_meta/FNN-default_rigids_meta.json',
            'HT-default': 'rigids_meta/HT-default_rigids_meta.json',
            'Ani-default': 'rigids_meta/Ani-default_rigids_meta.json'
        },
        endpoint=os.getenv('OSS_ENDPOINT'),
        access_key=os.getenv('OSS_ACCESS_KEY'),
        secret_key=os.getenv('OSS_SECRET_KEY'),
        bucket_name='3dac',
        logger_cfg=__logger_cfg__
    ),
    blendshapes_meta_reader_cfg=dict(
        type="MinioFileReader",
        name="blendshapes_meta_reader",
        file_paths={
            'KQ-default': 'blendshapes_meta/KQ-default_blendshapes_meta.json',
            'FNN-default': 'blendshapes_meta/FNN-default_blendshapes_meta.json',
            'HT-default': 'blendshapes_meta/HT-default_blendshapes_meta.json',
            'Ani-default': 'blendshapes_meta/Ani-default_blendshapes_meta.json'
        },
        endpoint=os.getenv('OSS_ENDPOINT'),
        access_key=os.getenv('OSS_ACCESS_KEY'),
        secret_key=os.getenv('OSS_SECRET_KEY'),
        bucket_name='3dac',
        logger_cfg=__logger_cfg__
    ),
    cache_cfg=dict(
        type="LocalCache",
        logger_cfg=__logger_cfg__
    ),
    maintain_check_interval=60,
    logger_cfg=__logger_cfg__,
)
