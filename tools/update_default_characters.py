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

from dlp3d_web_backend.data_structures import CharacterConfig, UserConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


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
):
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
                logger.warning(f"Config file not found: {config_path}, "
                               f"skipping...")
                continue

            with open(config_path, encoding='utf-8') as f:
                character_config_dict = json.load(f)

            character_name = character_config_dict.get("character_name")
            if not character_name:
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
                logger.info(f"Created character: {character_name} "
                            f"(character_id: {character_id})")


def main():
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
        required=True,
        help="User ID to update characters for"
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
        )
    )


if __name__ == "__main__":
    main()
