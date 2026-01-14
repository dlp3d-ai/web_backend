#!/usr/bin/env python3
import argparse
import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime

import pytz
from pymongo import AsyncMongoClient
from tqdm import tqdm

from dlp3d_web_backend.data_structures import CharacterConfig, UserConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


async def get_all_user_ids(
    mongodb_host: str,
    mongodb_port: int,
    mongodb_username: str,
    mongodb_password: str,
    mongodb_database: str,
    mongodb_auth_database: str,
    mongodb_user_collection: str = 'UserConfigs',
) -> list[str]:
    """Retrieve all user IDs from MongoDB user collection.

    Args:
        mongodb_host (str):
            MongoDB server host address.
        mongodb_port (int):
            MongoDB server port number.
        mongodb_username (str):
            MongoDB authentication username.
        mongodb_password (str):
            MongoDB authentication password.
        mongodb_database (str):
            MongoDB database name.
        mongodb_auth_database (str):
            MongoDB authentication database name.
        mongodb_user_collection (str, optional):
            MongoDB user collection name. Defaults to 'UserConfigs'.

    Returns:
        list[str]:
            List of all user IDs found in the database.
    """
    async with AsyncMongoClient(
        host=mongodb_host,
        port=mongodb_port,
        username=mongodb_username,
        password=mongodb_password,
        authSource=mongodb_auth_database,
    ) as client:
        db = client[mongodb_database]
        user_collection = db[mongodb_user_collection]
        cursor = user_collection.find({}, {"user_id": 1})
        user_ids = [
            doc["user_id"]
            async for doc in cursor
            if "user_id" in doc
        ]
        return user_ids


async def update_default_characters(
    mongodb_host: str,
    mongodb_port: int,
    mongodb_username: str,
    mongodb_password: str,
    mongodb_database: str,
    mongodb_auth_database: str,
    user_id: str,
    default_character_config_paths: list[str],
    mongodb_user_collection: str = 'UserConfigs',
    mongodb_character_collection: str = 'CharacterConfigs',
    silent: bool = False,
):
    """Update or create default characters for a specific user in MongoDB.

    This function processes character configuration files and updates or creates
    default characters in the database. If a character with the same name and
    read_only=True already exists, it will be updated. Otherwise, a new
    character will be created with a new character_id and current timestamp.

    Args:
        mongodb_host (str):
            MongoDB server host address.
        mongodb_port (int):
            MongoDB server port number.
        mongodb_username (str):
            MongoDB authentication username.
        mongodb_password (str):
            MongoDB authentication password.
        mongodb_database (str):
            MongoDB database name.
        mongodb_auth_database (str):
            MongoDB authentication database name.
        user_id (str):
            Target user ID to update characters for.
        default_character_config_paths (list[str]):
            List of file paths to character configuration JSON files.
        mongodb_user_collection (str, optional):
            MongoDB user collection name. Defaults to 'UserConfigs'.
        mongodb_character_collection (str, optional):
            MongoDB character collection name. Defaults to 'CharacterConfigs'.
        silent (bool, optional):
            If True, suppress log output. Defaults to False.

    Raises:
        ValueError:
            Raised when the specified user_id is not found in the database.
    """
    async with AsyncMongoClient(
        host=mongodb_host,
        port=mongodb_port,
        username=mongodb_username,
        password=mongodb_password,
        authSource=mongodb_auth_database,
    ) as client:
        db = client[mongodb_database]
        user_collection = db[mongodb_user_collection]
        character_collection = db[mongodb_character_collection]

        user_doc = await user_collection.find_one({"user_id": user_id})
        if user_doc is None:
            raise ValueError(f"User {user_id} not found in database")

        user_config = UserConfig.model_validate(user_doc)
        timezone = pytz.timezone(user_config.timezone)

        for config_path in default_character_config_paths:
            if not os.path.exists(config_path):
                if not silent:
                    logger.warning(f"Config file not found: {config_path}, "
                                   f"skipping...")
                continue

            with open(config_path, encoding='utf-8') as f:
                character_config_dict = json.load(f)

            character_name = character_config_dict.get("character_name")
            if not character_name:
                if not silent:
                    logger.warning(f"character_name not found in {config_path}, "
                                   f"skipping...")
                continue

            existing_doc = await character_collection.find_one({
                "user_id": user_id,
                "character_name": character_name,
                "read_only": True
            })

            if existing_doc:
                character_id = existing_doc.get("character_id")
                create_datatime = existing_doc.get("create_datatime")

                character_config_dict["user_id"] = user_id
                character_config_dict["character_id"] = character_id
                character_config_dict["create_datatime"] = create_datatime
                character_config_dict["read_only"] = True

                character_config = CharacterConfig.model_validate(
                    character_config_dict)
                await character_collection.replace_one(
                    {"user_id": user_id,
                     "character_name": character_name,
                     "read_only": True},
                    character_config.model_dump()
                )
                if not silent:
                    logger.info(f"Updated character: {character_name} "
                               f"(character_id: {character_id})")
            else:
                character_id = str(uuid.uuid4())
                unix_timestamp = time.time()
                time_str = datetime.fromtimestamp(
                    unix_timestamp, timezone
                ).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

                character_config_dict["user_id"] = user_id
                character_config_dict["character_id"] = character_id
                character_config_dict["create_datatime"] = time_str
                character_config_dict["read_only"] = True

                character_config = CharacterConfig.model_validate(
                    character_config_dict)
                await character_collection.insert_one(
                    character_config.model_dump())
                if not silent:
                    logger.info(f"Created character: {character_name} "
                                f"(character_id: {character_id})")


def main():
    """Main entry point for the character update tool.

    This function parses command-line arguments, reads MongoDB connection
    details from environment variables, and either updates characters for a
    single user or prompts for confirmation to update all users. When updating
    all users, it displays a progress bar using tqdm.

    Environment Variables:
        MONGODB_HOST: MongoDB server host address.
        MONGODB_PORT: MongoDB server port number (default: 27017).
        MONGODB_USERNAME: MongoDB authentication username.
        MONGODB_PASSWORD: MongoDB authentication password.
        MONGODB_DATABASE: MongoDB database name.
        MONGODB_AUTH_DATABASE: MongoDB authentication database name.

    Raises:
        ValueError:
            Raised when required environment variables are missing or when
            the character config paths file does not contain a valid list.
    """
    parser = argparse.ArgumentParser(
        description="Update default characters in MongoDB"
    )
    parser.add_argument(
        "--default-character-config-paths",
        type=str,
        required=True,
        help="Path to JSON file containing list of character config paths"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        required=False,
        default=None,
        help="User ID to update characters for. If not specified, "
             "will prompt to update all users."
    )
    parser.add_argument(
        "--mongodb-user-collection",
        type=str,
        default="UserConfigs",
        help="MongoDB user collection name (default: UserConfigs)"
    )
    parser.add_argument(
        "--mongodb-character-collection",
        type=str,
        default="CharacterConfigs",
        help="MongoDB character collection name (default: CharacterConfigs)"
    )

    args = parser.parse_args()

    mongodb_host = os.getenv("MONGODB_HOST")
    mongodb_port = int(os.getenv("MONGODB_PORT", 27017))
    mongodb_username = os.getenv("MONGODB_USERNAME")
    mongodb_password = os.getenv("MONGODB_PASSWORD")
    mongodb_database = os.getenv("MONGODB_DATABASE")
    mongodb_auth_database = os.getenv("MONGODB_AUTH_DATABASE")

    required_vars = [
        mongodb_host, mongodb_username, mongodb_password,
        mongodb_database, mongodb_auth_database
    ]
    if not all(required_vars):
        raise ValueError(
            "Missing required environment variables: "
            "MONGODB_HOST, MONGODB_USERNAME, MONGODB_PASSWORD, "
            "MONGODB_DATABASE, MONGODB_AUTH_DATABASE"
        )

    with open(args.default_character_config_paths,
              encoding='utf-8') as f:
        default_character_config_paths = json.load(f)

    if not isinstance(default_character_config_paths, list):
        raise ValueError(
            f"Expected list in {args.default_character_config_paths}, "
            f"got {type(default_character_config_paths).__name__}"
        )

    if args.user_id is not None:
        asyncio.run(
            update_default_characters(
                mongodb_host=mongodb_host,
                mongodb_port=mongodb_port,
                mongodb_username=mongodb_username,
                mongodb_password=mongodb_password,
                mongodb_database=mongodb_database,
                mongodb_auth_database=mongodb_auth_database,
                user_id=args.user_id,
                default_character_config_paths=default_character_config_paths,
                mongodb_user_collection=args.mongodb_user_collection,
                mongodb_character_collection=args.mongodb_character_collection,
                silent=False,
            )
        )
    else:
        logger.warning("No user_id specified.")
        logger.warning("This will update default characters for ALL users in "
                       "the database.")
        response = input("Do you want to proceed? (Y/N): ").strip().upper()

        if response != 'Y':
            logger.info("Operation cancelled. No changes were made.")
            return

        async def update_single_user(user_id: str) -> None:
            """Update default characters for a single user with error handling.

            Args:
                user_id (str):
                    User ID to update characters for.
            """
            try:
                await update_default_characters(
                    mongodb_host=mongodb_host,
                    mongodb_port=mongodb_port,
                    mongodb_username=mongodb_username,
                    mongodb_password=mongodb_password,
                    mongodb_database=mongodb_database,
                    mongodb_auth_database=mongodb_auth_database,
                    user_id=user_id,
                    default_character_config_paths=default_character_config_paths,
                    mongodb_user_collection=args.mongodb_user_collection,
                    mongodb_character_collection=args.mongodb_character_collection,
                    silent=True,
                )
            except Exception as e:
                tqdm.write(f"Error updating user {user_id}: {e}")

        async def update_all_users():
            """Update default characters for all users in the database.

            This function retrieves all user IDs, displays them, and then
            updates characters for each user with progress tracking using tqdm.
            """
            user_ids = await get_all_user_ids(
                mongodb_host=mongodb_host,
                mongodb_port=mongodb_port,
                mongodb_username=mongodb_username,
                mongodb_password=mongodb_password,
                mongodb_database=mongodb_database,
                mongodb_auth_database=mongodb_auth_database,
                mongodb_user_collection=args.mongodb_user_collection,
            )

            if not user_ids:
                logger.warning("No users found in database.")
                return

            logger.info(f"Found {len(user_ids)} users")

            logger.info("Starting update process...")
            for user_id in tqdm(user_ids, desc="Updating users"):
                await update_single_user(user_id)

            logger.info("Finished updating all users.")

        asyncio.run(update_all_users())


if __name__ == "__main__":
    main()
