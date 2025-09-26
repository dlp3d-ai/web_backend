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
mongodb_host = 'mongodb'
mongodb_username = 'orchestrator'
mongodb_password = 'orchestrator_password'
mongodb_port = 27017
mongodb_database = 'web'
mongodb_auth_database = 'web'
default_character_config_paths = [
    'configs/kq-default_sample.json', 'configs/ani-default_sample.json']
enable_cors = False
host = '0.0.0.0'
port = 18080
logger_cfg = __logger_cfg__
