import os

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
    'configs/kq-default_sample.json', 'configs/ani-default_sample.json']
default_user_config_path = 'secrets/user_sample.json'
enable_cors = False
host = '0.0.0.0'
port = 8080
logger_cfg = __logger_cfg__
