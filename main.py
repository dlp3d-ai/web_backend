import argparse
import logging
import os
import sys

from pymongo import MongoClient

from dlp3d_web_backend.service.server import FastAPIServer
from dlp3d_web_backend.utils.config import file2dict
from dlp3d_web_backend.utils.log import setup_logger


def main(args) -> int:
    """Main entry point for the web backend application.

    This function initializes the application by loading configuration,
    setting up logging, testing MongoDB connection and permissions,
    and starting the appropriate server instance.

    Args:
        args:
            Parsed command line arguments containing configuration path.

    Returns:
        int:
            Exit code (0 for success).
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    startup_config = file2dict(args.config_path)
    mongodb_host = startup_config['mongodb_host']
    mongodb_username = startup_config['mongodb_username']
    mongodb_password = startup_config['mongodb_password']
    mongodb_port = startup_config['mongodb_port']
    mongodb_database = startup_config['mongodb_database']
    mongodb_auth_database = startup_config['mongodb_auth_database']
    if args.mongodb_admin_username is None:
        admin_usename = os.environ.get('MONGODB_ADMIN_USERNAME', 'admin')
    else:
        admin_usename = args.mongodb_admin_username
    if args.mongodb_admin_password is None:
        admin_password = os.environ.get('MONGODB_ADMIN_PASSWORD', '')
    else:
        admin_password = args.mongodb_admin_password
    logger_cfg = startup_config['logger_cfg'].copy()
    logger_cfg['logger_name'] = 'main'
    logger = setup_logger(**logger_cfg)

    # Test MongoDB connection and permissions first
    if test_mongodb(
            mongodb_host,
            mongodb_username,
            mongodb_password,
            mongodb_port,
            mongodb_database,
            mongodb_auth_database,
            logger):
        logger.info("MongoDB connection and permissions test passed, skipping setup")
    else:
        logger.info("MongoDB connection or permissions test failed, running setup")
        try:
            setup_mongodb(
                mongodb_host,
                mongodb_username,
                mongodb_password,
                mongodb_port,
                mongodb_database,
                mongodb_auth_database,
                admin_usename,
                admin_password,
                logger)
        except Exception as e:
            logger.error(f"Failed to setup MongoDB: {e!s}")
            raise
    # init server
    cls_name = startup_config.pop('type')
    if cls_name == 'FastAPIServer':
        server = FastAPIServer(**startup_config)
    else:
        raise ValueError(f'Invalid server type: {cls_name}')
    server.run()
    return 0

def test_mongodb(
        mongodb_host: str,
        mongodb_username: str,
        mongodb_password: str,
        mongodb_port: int,
        mongodb_database: str,
        mongodb_auth_database: str,
        logger: logging.Logger) -> bool:
    """Test MongoDB connection and permissions for the target user.

    This function tests if the target user can connect to MongoDB using the
    specified auth database and has read/write permissions on the target database.

    Args:
        mongodb_host (str):
            MongoDB server hostname.
        mongodb_username (str):
            Target username to test.
        mongodb_password (str):
            Password for the target user.
        mongodb_port (int):
            MongoDB server port.
        mongodb_database (str):
            Target database name to test permissions on.
        mongodb_auth_database (str):
            Authentication database name.
        logger (logging.Logger):
            Logger instance for recording test results.

    Returns:
        bool:
            True if connection and permissions test passes, False otherwise.
    """
    try:
        # Test connection with target user credentials
        with MongoClient(
                host=mongodb_host,
                port=mongodb_port,
                username=mongodb_username,
                password=mongodb_password,
                authSource=mongodb_auth_database) as client:

            # Test read permission by listing collections
            db = client[mongodb_database]
            collections = db.list_collection_names()
            logger.debug(
                f"Successfully listed collections in {mongodb_database}: {collections}")

            # Test write permission by creating a temporary collection
            test_collection = db['_test_permissions']
            test_collection.insert_one(
                {"test": "permission_check", "timestamp": "temp"})
            test_collection.drop()
            logger.debug(f"Successfully tested write permissions on {mongodb_database}")

            return True

    except Exception as e:
        logger.warning(f"MongoDB connection/permission test failed: {e!s}")
        return False

def setup_mongodb(
        mongodb_host: str,
        mongodb_username: str,
        mongodb_password: str,
        mongodb_port: int,
        mongodb_database: str,
        mongodb_auth_database: str,
        admin_usename: str,
        admin_password: str,
        logger: logging.Logger) -> None:
    """Setup MongoDB database and user.

    This function checks if the target database exists and creates it if not.
    It also checks if the target user exists in the auth database and creates
    the user with full permissions on the target database if not.

    Args:
        mongodb_host (str):
            MongoDB server hostname.
        mongodb_username (str):
            Target username to create or verify.
        mongodb_password (str):
            Password for the target user.
        mongodb_port (int):
            MongoDB server port.
        mongodb_database (str):
            Target database name to create or verify.
        mongodb_auth_database (str):
            Authentication database name.
        admin_usename (str):
            Admin username for MongoDB connection.
        admin_password (str):
            Admin password for MongoDB connection.
        logger (logging.Logger):
            Logger instance for recording operations.
    """
    with MongoClient(
            host=mongodb_host,
            port=mongodb_port,
            username=admin_usename,
            password=admin_password) as client:
        # Check if target database exists
        database_list = client.list_database_names()
        if mongodb_database not in database_list:
            # Create database by creating a collection and then dropping it
            db = client[mongodb_database]
            db.create_collection('_temp_setup')
            db.drop_collection('_temp_setup')
            logger.info(f"Created database: {mongodb_database}")
        else:
            logger.info(
                f"Database {mongodb_database} already exists, skipping creation")

        # Check if target user exists in auth database
        auth_db = client[mongodb_auth_database]
        try:
            # Try to find the user in the system.users collection
            user_exists = auth_db.command("usersInfo", mongodb_username)
            if user_exists['users']:
                logger.info(
                    f"User {mongodb_username} already exists " +\
                    f"in auth database {mongodb_auth_database}")
            else:
                raise Exception("User not found")
        except Exception:
            # User doesn't exist, create it
            try:
                auth_db.command("createUser", mongodb_username,
                              pwd=mongodb_password,
                              roles=[{"role": "readWrite", "db": mongodb_database}])
                logger.info(
                    f"Created user {mongodb_username} with " +\
                    f"readWrite permissions on database {mongodb_database}")
            except Exception as e:
                logger.error(f"Failed to create user {mongodb_username}: {e!s}")
                raise

def setup_parser():
    """Set up command line argument parser for the application.

    This function creates and configures an argument parser to handle
    command line arguments for the application, including configuration
    file path specification.

    Returns:
        argparse.Namespace:
            Parsed command line arguments containing configuration
            file path and other application settings.
    """
    parser = argparse.ArgumentParser(
        description='Start the web backend server program.',
        epilog='Example: python main.py --config_path configs/production.py'
    )
    # server args
    parser.add_argument(
        '--config_path',
        type=str,
        help='Path to the configuration file containing server settings, ' +
        'database connections, and API configurations. ' +
        'The config file should be a Python module that ' +
        'exports a dictionary with server parameters.',
        default='configs/local.py')
    parser.add_argument(
        '--mongodb_admin_username',
        type=str,
        required=False,
        default=None,
        help='MongoDB admin username for database setup operations. ' +
        'If not provided, will use MONGODB_ADMIN_USERNAME environment variable ' +
        'or default to "admin". This is used for creating databases and users ' +
        'when the target user does not have sufficient permissions.')
    parser.add_argument(
        '--mongodb_admin_password',
        type=str,
        required=False,
        default=None,
        help='MongoDB admin password for database setup operations. ' +
        'If not provided, will use MONGODB_ADMIN_PASSWORD environment variable ' +
        'or default to empty string. This is used for creating databases and users ' +
        'when the target user does not have sufficient permissions.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = setup_parser()
    ret_val = main(args)
    sys.exit(ret_val)
