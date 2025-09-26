import json
import os
import time
import uuid
from datetime import datetime
from typing import Any

import pytz
import uvicorn
from fastapi import (
    APIRouter,
    FastAPI,
    Request,
    Response,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import AsyncMongoClient, MongoClient

from ..data_structures import CharacterConfig, UserConfig, UserCredential
from ..utils.super import Super
from .exceptions import (
    OPENAPI_RESPONSE_400,
    OPENAPI_RESPONSE_404,
    OPENAPI_RESPONSE_503,
    AuthenticationFailedException,
    NoCharacterException,
    NoLogFileException,
    NoUserException,
    ReadOnlyCharacterException,
    UserAlreadyExistsException,
    UsernameNotFoundException,
    register_error_handlers,
)
from .requests import (
    AuthenticateUserRequest,
    CreateUserRequest,
    DeleteCharacterRequest,
    DeleteUserRequest,
    DuplicateCharacterRequest,
    RegisterUserRequest,
    UpdateCharacterASRRequest,
    UpdateCharacterAvatarRequest,
    UpdateCharacterClassificationRequest,
    UpdateCharacterConversationRequest,
    UpdateCharacterMemoryRequest,
    UpdateCharacterNameRequest,
    UpdateCharacterPromptRequest,
    UpdateCharacterReactionRequest,
    UpdateCharacterSceneRequest,
    UpdateCharacterTTSRequest,
    UpdateUserConfigRequest,
    UpdateUserPasswordRequest,
)
from .responses import (
    AuthenticateUserResponse,
    DuplicateCharacterResponse,
    GetAvailableProvidersResponse,
    GetCharacterConfigResponse,
    GetCharacterListResponse,
    ListUsersResponse,
    RegisterUserResponse,
)


class FastAPIServer(Super):
    """FastAPI server for handling HTTP requests and WebSocket connections.

    This server provides endpoints for user management, character configuration,
    health checks, and log file access through HTTP protocols.
    """

    def __init__(
        self,
        mongodb_host: str,
        mongodb_username: str,
        mongodb_password: str,
        default_character_config_paths: list[str],
        mongodb_port: int = 27017,
        mongodb_database: str = 'web',
        mongodb_auth_database: str = 'admin',
        mongodb_credential_collection: str = 'UserCredentials',
        mongodb_user_collection: str = 'UserConfigs',
        mongodb_character_collection: str = 'CharacterConfigs',
        default_user_config_path: str | None = None,
        enable_cors: bool = False,
        host: str = '0.0.0.0',
        port: int = 80,
        startup_event_listener: None | list = None,
        shutdown_event_listener: None | list = None,
        logger_cfg: None | dict = None,
    ) -> None:
        """Initialize the FastAPI server.

        Args:
            mongodb_host (str):
                MongoDB server hostname.
            mongodb_username (str):
                MongoDB authentication username.
            mongodb_password (str):
                MongoDB authentication password.
            default_character_config_paths (list[str]):
                List of file paths to default character configuration JSON files.
            mongodb_port (int, optional):
                MongoDB server port. Defaults to 27017.
            mongodb_database (str, optional):
                MongoDB database name. Defaults to 'web'.
            mongodb_auth_database (str, optional):
                MongoDB authentication database. Defaults to 'admin'.
            mongodb_credential_collection (str, optional):
                MongoDB collection name for user credentials.
                Defaults to 'UserCredentials'.
            mongodb_user_collection (str, optional):
                MongoDB collection name for user configurations.
                Defaults to 'UserConfigs'.
            mongodb_character_collection (str, optional):
                MongoDB collection name for character configurations.
                Defaults to 'CharacterConfigs'.
            default_user_config_path (str | None, optional):
                Path to default user configuration JSON file. Defaults to None.
            enable_cors (bool, optional):
                Whether to enable CORS middleware. Defaults to False.
            host (str, optional):
                Host to run this service. Defaults to '0.0.0.0'.
            port (int, optional):
                Port to run this service. Defaults to 80.
            startup_event_listener (None | list, optional):
                Event listeners for startup. Defaults to None.
            shutdown_event_listener (None | list, optional):
                Event listeners for shutdown. Defaults to None.
            logger_cfg (None | dict, optional):
                Logger configuration. Defaults to None.
        """
        Super.__init__(self, logger_cfg=logger_cfg)
        self.mongodb_host = mongodb_host
        self.mongodb_username = mongodb_username
        self.mongodb_password = mongodb_password
        self.mongodb_port = mongodb_port
        self.mongodb_database = mongodb_database
        self.mongodb_auth_database = mongodb_auth_database
        self.mongodb_credential_collection = mongodb_credential_collection
        self.mongodb_user_collection = mongodb_user_collection
        self.mongodb_character_collection = mongodb_character_collection
        # test auth with MongoClient
        with MongoClient(
            host=self.mongodb_host,
            port=self.mongodb_port,
            username=self.mongodb_username,
            password=self.mongodb_password,
            authSource=self.mongodb_auth_database,
        ) as client:
            client.admin.command("ping")
        # for default user config
        self.default_user_config: dict[str, str] = dict()
        if default_user_config_path is not None:
            with open(default_user_config_path) as f:
                self.default_user_config = json.load(f)
        # for default characters
        self.default_character_configs: list[dict[str, Any]] = list()
        for json_path in default_character_config_paths:
            with open(json_path) as f:
                data = json.load(f)
                self.default_character_configs.append(data)
        # for fastapi
        self.host = host
        self.port = port
        # for tailing the log file
        log_path = None
        for logger_handler in self.logger.handlers:
            if hasattr(logger_handler, "baseFilename"):
                log_path = logger_handler.baseFilename
                break
        self.log_path = log_path
        self.templates = Jinja2Templates(directory="templates")
        self.app = FastAPI()
        self.enable_cors = enable_cors
        if self.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            )
        if startup_event_listener is not None:
            for listener in startup_event_listener:
                self.app.add_event_handler('startup', listener)
        if shutdown_event_listener is not None:
            for listener in shutdown_event_listener:
                self.app.add_event_handler('shutdown', listener)
        register_error_handlers(self.app)
        self.asyncio_tasks = set()

    def _add_api_routes(self, router: APIRouter) -> None:
        """Add API routes to the router.

        This method registers all HTTP endpoints with the provided FastAPI router,
        including user management, character configuration, health checks,
        and log file access endpoints.

        Args:
            router (APIRouter):
                FastAPI router to add routes to.
        """
        # GET routes
        router.add_api_route(
            "/api/v1/list_characters/{user_id}",
            self.list_characters,
            methods=["GET"],
            response_model=GetCharacterListResponse,
        )
        router.add_api_route(
            "/api/v1/get_character_config/{user_id}/{character_id}",
            self.get_character_config,
            methods=["GET"],
            response_model=GetCharacterConfigResponse,
            responses={
                200: {
                    "description": "Success",
                    "model": GetCharacterConfigResponse
                },
                **OPENAPI_RESPONSE_404
            }
        )
        router.add_api_route(
            "/api/v1/get_available_llm/{user_id}",
            self.get_available_llm,
            methods=["GET"],
            response_model=GetAvailableProvidersResponse,
        )
        router.add_api_route(
            "/api/v1/get_available_asr/{user_id}",
            self.get_available_asr,
            methods=["GET"],
            response_model=GetAvailableProvidersResponse,
        )
        router.add_api_route(
            "/api/v1/get_available_tts/{user_id}",
            self.get_available_tts,
            methods=["GET"],
            response_model=GetAvailableProvidersResponse,
        )
        router.add_api_route(
            "/api/v1/list_users",
            self.list_users,
            methods=["GET"],
            response_model=ListUsersResponse,
        )
        router.add_api_route(
            "/api/v1/list_user_credential_id",
            self.list_user_credential_id,
            methods=["GET"],
            response_model=ListUsersResponse,
        )
        router.add_api_route(
            "/api/v1/list_user_config_id",
            self.list_user_config_id,
            methods=["GET"],
            response_model=ListUsersResponse,
        )
        # POST routes
        router.add_api_route(
            "/api/v1/register_user",
            self.register_user,
            methods=["POST"],
            response_model=RegisterUserResponse,
            responses={
                200: {
                    "description": "Success",
                    "model": RegisterUserResponse
                },
                **OPENAPI_RESPONSE_400
            },
        )
        router.add_api_route(
            "/api/v1/update_user_password",
            self.update_user_password,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_400
            },
        )
        router.add_api_route(
            "/api/v1/authenticate_user",
            self.authenticate_user,
            methods=["POST"],
            response_model=AuthenticateUserResponse,
            responses={
                200: {
                    "description": "Success",
                    "model": AuthenticateUserResponse
                },
                **OPENAPI_RESPONSE_400
            },
        )
        router.add_api_route(
            "/api/v1/create_user",
            self.create_user,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_400
            },
        )
        router.add_api_route(
            "/api/v1/duplicate_character",
            self.duplicate_character,
            methods=["POST"],
            response_model=DuplicateCharacterResponse,
            responses={
                200: {
                    "description": "Success",
                    "model": DuplicateCharacterResponse
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_name",
            self.update_character_name,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_scene",
            self.update_character_scene,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_prompt",
            self.update_character_prompt,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_asr",
            self.update_character_asr,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_tts",
            self.update_character_tts,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_classification",
            self.update_character_classification,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_conversation",
            self.update_character_conversation,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_reaction",
            self.update_character_reaction,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_character_memory",
            self.update_character_memory,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/update_user_config",
            self.update_user_config,
            methods=["POST"],
        )
        router.add_api_route(
            "/api/v1/delete_user",
            self.delete_user,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/api/v1/delete_character",
            self.delete_character,
            methods=["POST"],
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_404
            },
        )
        router.add_api_route(
            "/",
            self.root,
            methods=["GET"],
        )
        router.add_api_route(
            '/health',
            endpoint=self.health,
            status_code=200,
            methods=['GET'],
        )
        router.add_api_route(
            "/tail_log/{n_lines}",
            self.tail_log,
            methods=["GET"],
            status_code=200,
            response_model=str,
            responses={
                200: {
                    "description": "Success",
                    "model": str
                },
                **OPENAPI_RESPONSE_503
            },
        )
        router.add_api_route(
            "/dowload_log_file",
            self.dowload_log_file,
            methods=["GET"],
            status_code=200,
            responses={
                200: {
                    "description": "Success"
                },
                **OPENAPI_RESPONSE_503
            },
        )

    def run(self) -> None:
        """Run this FastAPI service according to configuration.

        This method starts the uvicorn server with the configured
        host, port, and application settings.
        """
        router = APIRouter()
        self._add_api_routes(router)
        self.app.include_router(router)
        uvicorn.run(self.app, host=self.host, port=self.port)

    async def list_users(self) -> ListUsersResponse:
        """Retrieve a list of all users with their credentials.

        This method connects to MongoDB and retrieves all users from the
        credential collection, returning both user IDs and usernames.

        Returns:
            ListUsersResponse:
                Response containing lists of user IDs and usernames.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_credential_collection]
            users = await collection.find(
                {}, {"_id": 0, "user_id": 1, "username": 1}).to_list(length=None)
        username_list = list()
        user_id_list = list()
        for user in users:
            user_id_list.append(user["user_id"])
            username_list.append(user["username"])
        response = ListUsersResponse(
            user_id_list=user_id_list,
            user_name_list=username_list,
        )
        return response

    async def list_user_credential_id(self) -> ListUsersResponse:
        """Retrieve a list of user IDs from the credential collection.

        This method connects to MongoDB and retrieves only the user IDs
        from the credential collection, excluding usernames.

        Returns:
            ListUsersResponse:
                Response containing a list of user IDs.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_credential_collection]
            users = await collection.find(
                {}, {"_id": 0, "user_id": 1,}).to_list(length=None)
        response = ListUsersResponse(
            user_id_list=[user["user_id"] for user in users])
        return response

    async def list_user_config_id(self) -> ListUsersResponse:
        """Retrieve a list of user IDs from the user configuration collection.

        This method connects to MongoDB and retrieves only the user IDs
        from the user configuration collection.

        Returns:
            ListUsersResponse:
                Response containing a list of user IDs.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_user_collection]
            users = await collection.find(
                {}, {"_id": 0, "user_id": 1,}).to_list(length=None)
        response = ListUsersResponse(
            user_id_list=[user["user_id"] for user in users])
        return response

    async def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        """Register a new user with username and password.

        This method creates a new user account by generating a unique user ID,
        checking for username conflicts, and storing the credentials in the
        credential collection.

        Args:
            request (RegisterUserRequest):
                Request containing username and password for the new user.

        Returns:
            RegisterUserResponse:
                Response containing the generated user ID.

        Raises:
            UserAlreadyExistsException:
                If the username already exists in the system.
        """
        user_id = str(uuid.uuid4())
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            credential_collection = db[self.mongodb_credential_collection]
            # check if username already exists
            if await credential_collection.count_documents(
                    {"username": request.username}) > 0:
                msg = f"Username {request.username} already exists."
                self.logger.error(msg)
                raise UserAlreadyExistsException(status_code=400, detail=msg)
            credential = UserCredential(
                username=request.username,
                password=request.password,
                user_id=user_id)
            await credential_collection.insert_one(credential.model_dump())
        return RegisterUserResponse(user_id=user_id)

    async def create_user(self, create_user_request: CreateUserRequest) -> Response:
        """Create a new user with default configuration and characters.

        This method generates a new user with a unique ID, creates a user
        configuration with default settings, and initializes default
        character configurations for the user.

        Args:
            create_user_request (CreateUserRequest):
                Request containing the user ID to create.

        Returns:
            Response:
                Empty response indicating successful creation.

        Raises:
            UserAlreadyExistsException:
                If a user with the specified ID already exists.
        """
        user_id = create_user_request.user_id
        user_config_dict = self.default_user_config.copy()
        user_config_dict["user_id"] = user_id
        user_config = UserConfig.model_validate(user_config_dict)
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            user_collection = db[self.mongodb_user_collection]
            # check if user already exists
            if await user_collection.count_documents({"user_id": user_id}) > 0:
                msg = f"User {user_id} already exists."
                self.logger.error(msg)
                raise UserAlreadyExistsException(status_code=400, detail=msg)
            await user_collection.insert_one(user_config.model_dump())
            character_collection = db[self.mongodb_character_collection]
            for character in self.default_character_configs:
                character_id = str(uuid.uuid4())
                unix_timestamp = time.time()
                shanghai_tz = pytz.timezone("Asia/Shanghai")
                time_str = datetime.fromtimestamp(
                    unix_timestamp, shanghai_tz).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
                character_config_dict = character.copy()
                character_config_dict["user_id"] = user_id
                character_config_dict["character_id"] = character_id
                character_config_dict["create_datatime"] = time_str
                character_config_dict["read_only"] = True
                character_config = CharacterConfig.model_validate(character_config_dict)
                await character_collection.insert_one(character_config.model_dump())
        return Response()

    async def update_user_password(
            self,
            request: UpdateUserPasswordRequest) -> Response:
        """Update a user's password after authentication.

        This method verifies the user's current password and updates it
        with a new password in the credential collection.

        Args:
            request (UpdateUserPasswordRequest):
                Request containing username, current password, and new password.

        Returns:
            Response:
                Empty response indicating successful password update.

        Raises:
            AuthenticationFailedException:
                If the current password is incorrect.
            UsernameNotFoundException:
                If the username is not found.
        """
        username = request.username
        old_password = request.password
        await self.authenticate_user(
            AuthenticateUserRequest(username=username, password=old_password))
        new_password = request.new_password
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            credential_collection = db[self.mongodb_credential_collection]
            await credential_collection.update_one(
                {"username": username},
                {"$set": {"password": new_password}})
        return Response()

    async def authenticate_user(
            self,
            request: AuthenticateUserRequest) -> AuthenticateUserResponse:
        """Authenticate user with username and password.

        This method verifies user credentials against the credential collection
        and returns the user ID if authentication is successful.

        Args:
            request (AuthenticateUserRequest):
                Request containing username and password for authentication.

        Returns:
            AuthenticateUserResponse:
                Response containing the user ID if authentication successful.

        Raises:
            UsernameNotFoundException:
                If the username is not found.
            AuthenticationFailedException:
                If the password is incorrect.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            credential_collection = db[self.mongodb_credential_collection]
            username_hit = await credential_collection.find_one(
                {"username": request.username})
            if username_hit is None:
                msg = f"Username {request.username} not found."
                self.logger.error(msg)
                raise UsernameNotFoundException(status_code=400, detail=msg)
            password_hit = await credential_collection.find_one(
                {"username": request.username, "password": request.password})
            if password_hit is None:
                msg = "Password mismatch."
                self.logger.error(msg)
                raise AuthenticationFailedException(status_code=400, detail=msg)
            user_id = username_hit["user_id"]
            return AuthenticateUserResponse(user_id=user_id)

    async def delete_user(self, request: DeleteUserRequest) -> Response:
        """Delete a user and all associated data from the database.

        This method connects to MongoDB and performs a comprehensive delete operation.
        It deletes the user from three collections: credential collection (user
        credentials), user configuration collection (API keys and settings), and
        character collection (all characters associated with the user). The operation
        includes detailed logging for audit purposes and only raises an exception if
        no data is found for the user in any of the collections.

        Args:
            request (DeleteUserRequest):
                Request containing user ID to delete.

        Returns:
            Response:
                Empty response indicating successful deletion.

        Raises:
            NoUserException:
                If no user data is found in any collection for the specified user_id.
        """
        user_id = request.user_id
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            exception_msg = ''
            db = client[self.mongodb_database]
            credential_collection = db[self.mongodb_credential_collection]
            n_credentials = await credential_collection.count_documents({})
            if n_credentials == 0:
                exception_msg += f'No user credential found for user_id: {user_id}.\n'
            else:
                await credential_collection.delete_many({"user_id": user_id})
                self.logger.info(
                    f"Deleted user credential for user {user_id} from the database.")
            user_config_collection = db[self.mongodb_user_collection]
            # log how many documents are deleted
            n_user_configs = await user_config_collection.count_documents({})
            if n_user_configs == 0:
                exception_msg += f'No user config found for user_id: {user_id}.\n'
            else:
                await user_config_collection.delete_many({"user_id": user_id})
                self.logger.info(
                    f"Deleted user config for user {user_id} from the database.")
            character_collection = db[self.mongodb_character_collection]
            n_characters = await character_collection.count_documents(
                {"user_id": user_id})
            await character_collection.delete_many({"user_id": user_id})
            self.logger.info(
                f"Deleted {n_characters} characters for user {user_id}.")
            if len(exception_msg) > 0:
                self.logger.error(exception_msg)
                raise NoUserException(status_code=404, detail=exception_msg)
        response = Response()
        return response

    async def duplicate_character(
            self, request: DuplicateCharacterRequest) -> DuplicateCharacterResponse:
        """Duplicate a character.

        Args:
            request (DuplicateCharacterRequest):
                Request containing user ID and character ID to duplicate.

        Returns:
            DuplicateCharacterResponse:
                Response containing the new character ID.
        """
        new_character_id = str(uuid.uuid4())
        new_character_name = request.character_name
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            character = await collection.find_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"_id": 0})
            character_config_dict = character.copy()
            character_config_dict["character_id"] = new_character_id
            character_config_dict["read_only"] = False
            if new_character_name is not None:
                character_config_dict["character_name"] = new_character_name
            character_config = CharacterConfig.model_validate(character_config_dict)
            await collection.insert_one(character_config.model_dump())
        return DuplicateCharacterResponse(character_id=new_character_id)

    async def list_characters(
            self,
            user_id: str) -> GetCharacterListResponse:
        """Retrieve a list of characters for a specific user.

        Args:
            user_id (str):
                Unique identifier of the user.

        Returns:
            GetCharacterListResponse:
                Response containing lists of character IDs and names.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            characters = await collection.find(
                {"user_id": user_id},
                {"_id": 0, "character_id": 1, "character_name": 1}
                ).to_list(length=None)
        response = GetCharacterListResponse(
            character_id_list=[
                character["character_id"] for character in characters],
            character_name_list=[
                character["character_name"] for character in characters]
        )
        return response

    async def get_character_config(
            self,
            user_id: str,
            character_id: str) -> GetCharacterConfigResponse:
        """Retrieve complete configuration for a specific character.

        Args:
            user_id (str):
                Unique identifier of the user.
            character_id (str):
                Unique identifier of the character.

        Returns:
            GetCharacterConfigResponse:
                Complete character configuration data.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(client, user_id, character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            character = await collection.find_one(
                {"user_id": user_id,
                 "character_id": character_id},
                {"_id": 0})
        response = GetCharacterConfigResponse.model_validate(character)
        return response

    async def delete_character(self, request: DeleteCharacterRequest) -> Response:
        """Delete a character from the database.

        This method connects to MongoDB and removes a specific character from the
        character collection. It first verifies that the character exists before
        attempting deletion and logs the operation for audit purposes.

        Args:
            request (DeleteCharacterRequest):
                Request containing user ID and character ID to delete.

        Returns:
            Response:
                Empty response indicating successful deletion.

        Raises:
            NoCharacterException:
                If no character is found with the specified user_id and character_id.
        """
        async with AsyncMongoClient(
            host=self.mongodb_host,
            port=self.mongodb_port,
            username=self.mongodb_username,
            password=self.mongodb_password,
            authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            collection = db[self.mongodb_character_collection]
            await collection.delete_one(
                {"user_id": request.user_id, "character_id": request.character_id})
        response = Response()
        return response

    async def update_character_name(
            self, request: UpdateCharacterNameRequest) -> Response:
        """Update the name of a specific character.

        This method updates the character name for a given user and character ID.
        It first validates that the character exists and is not read-only before
        performing the update operation in the MongoDB database.

        Args:
            request (UpdateCharacterNameRequest):
                Request object containing user_id, character_id, and new character_name.

        Returns:
            Response:
                Empty response object indicating successful completion of the operation.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set": {"character_name": request.character_name}})
        response = Response()
        return response

    async def update_character_avatar(
            self, request: UpdateCharacterAvatarRequest) -> Response:
        """Update the avatar for a specific character.

        Args:
            request (UpdateCharacterAvatarRequest):
                Request containing user ID, character ID, and new avatar.

        Returns:
            Response:
                Empty response indicating successful update.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set": {"avatar": request.avatar}})
        response = Response()
        return response

    async def update_character_scene(
            self, request: UpdateCharacterSceneRequest) -> Response:
        """Update the scene configuration for a specific character.

        This method updates the scene name associated with a character in the
        database. It first checks if the character is read-only and raises an
        exception if modification is not allowed.

        Args:
            request (UpdateCharacterSceneRequest):
                Request containing user ID, character ID, and new scene name.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set": {"scene_name": request.scene_name}})
        response = Response()
        return response

    async def update_character_prompt(
            self,
            request: UpdateCharacterPromptRequest) -> Response:
        """Update the system prompt for a specific character.

        Args:
            request (UpdateCharacterPromptRequest):
                Request containing user ID, character ID, and new prompt.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set": {"prompt": request.prompt}})
        response = Response()
        return response

    async def update_character_asr(
            self,
            request: UpdateCharacterASRRequest) -> Response:
        """Update the ASR (Automatic Speech Recognition) adapter for a character.

        Args:
            request (UpdateCharacterASRRequest):
                Request containing user ID, character ID, and ASR adapter.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set": {"asr_adapter": request.asr_adapter}})
        response = Response()
        return response

    async def update_character_tts(
            self,
            request: UpdateCharacterTTSRequest) -> Response:
        """Update the TTS (Text-to-Speech) configuration for a character.

        Args:
            request (UpdateCharacterTTSRequest):
                Request containing user ID, character ID, TTS adapter,
                voice selection, and speech speed.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set":
                    {
                        "tts_adapter": request.tts_adapter,
                        "voice": request.voice,
                        "voice_speed": request.voice_speed}})
        response = Response()
        return response

    async def update_character_classification(
            self,
            request: UpdateCharacterClassificationRequest) -> Response:
        """Update the classification configuration for a character.

        Args:
            request (UpdateCharacterClassificationRequest):
                Request containing user ID, character ID, classification
                adapter, and optional model override.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set":
                    {
                        "classification_adapter":
                            request.classification_adapter,
                        "classification_model_override":
                            request.classification_model_override}})
        response = Response()
        return response

    async def update_character_conversation(
            self,
            request: UpdateCharacterConversationRequest) -> Response:
        """Update the conversation configuration for a character.

        Args:
            request (UpdateCharacterConversationRequest):
                Request containing user ID, character ID, conversation
                adapter, and optional model override.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set":
                    {
                        "conversation_adapter":
                            request.conversation_adapter,
                        "conversation_model_override":
                            request.conversation_model_override}})
        response = Response()
        return response

    async def update_character_reaction(
            self,
            request: UpdateCharacterReactionRequest) -> Response:
        """Update the reaction configuration for a character.

        Args:
            request (UpdateCharacterReactionRequest):
                Request containing user ID, character ID, reaction
                adapter, and optional model override.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set": {
                    "reaction_adapter": request.reaction_adapter,
                    "reaction_model_override": request.reaction_model_override}})
        response = Response()
        return response

    async def update_character_memory(
            self,
            request: UpdateCharacterMemoryRequest) -> Response:
        """Update the memory configuration for a character.

        Args:
            request (UpdateCharacterMemoryRequest):
                Request containing user ID, character ID, memory
                adapter, and optional model override.

        Returns:
            Response:
                Empty response indicating successful update.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            await self._check_character_exists(
                client, request.user_id, request.character_id)
            await self._check_character_read_only(
                client, request.user_id, request.character_id)
            db = client[self.mongodb_database]
            collection = db[self.mongodb_character_collection]
            await collection.update_one(
                {"user_id": request.user_id, "character_id": request.character_id},
                {"$set":
                    {
                        "memory_adapter":
                            request.memory_adapter,
                        "memory_model_override":
                            request.memory_model_override}})
        response = Response()
        return response

    async def update_user_config(
            self,
            request: UpdateUserConfigRequest) -> Response:
        """Update user API key configuration.

        This method updates only the non-None fields in the request,
        preserving existing values for fields that are None.

        Args:
            request (UpdateUserConfigRequest):
                Request containing user ID and API keys to update.
                Fields with None values will not be updated.

        Returns:
            Response:
                Empty response indicating successful update.
        """
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_user_collection]

            update_data = {
                field: value for field, value in request.model_dump().items()
                if field != "user_id" and value is not None
            }
            if update_data:
                await collection.update_one(
                    {"user_id": request.user_id},
                    {"$set": update_data})
        response = Response()
        return response

    async def get_available_llm(self, user_id: str) -> GetAvailableProvidersResponse:
        """Get available LLM services based on user's API key configuration.

        Args:
            user_id (str):
                Unique identifier of the user.

        Returns:
            GetAvailableProvidersResponse:
                Response containing set of available LLM service names.
        """
        llm_requirements = dict(
            openai={'openai_api_key'},
            xai={'xai_api_key'},
            anthropic={'anthropic_api_key'},
            gemini={'gemini_api_key'},
            deepseek={'deepseek_api_key'},
            sensenova={'sensenova_ak', 'sensenova_sk'},
        )
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_user_collection]
            api_keys = await collection.find_one(
                {"user_id": user_id},
                {"_id": 0})
        return_set = set()
        for key, value in llm_requirements.items():
            if all(api_keys.get(key) != '' for key in value):
                return_set.add(key)
        return GetAvailableProvidersResponse(options=return_set)

    async def get_available_asr(self, user_id: str) -> GetAvailableProvidersResponse:
        """Get available ASR (Automatic Speech Recognition) providers for a user.

        This method checks which ASR providers are available for the specified user
        based on their configured API keys. Providers that require no API keys
        (like zoetrope) are always available, while others require valid API keys
        to be configured in the user's profile.

        Args:
            user_id (str):
                Unique identifier of the user to check ASR availability for.

        Returns:
            GetAvailableProvidersResponse:
                Response containing a set of available ASR provider names.
        """
        asr_requirements = dict(
            openai={'openai_api_key'},
            zoetrope=set(),
            softsugar={'softsugar_app_id', 'softsugar_app_key'}
        )
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_user_collection]
            api_keys = await collection.find_one(
                {"user_id": user_id},
                {"_id": 0})
        return_set = set()
        for key, value in asr_requirements.items():
            if len(value) == 0:
                return_set.add(key)
            elif all(api_keys.get(key) != '' for key in value):
                return_set.add(key)
        return GetAvailableProvidersResponse(options=return_set)

    async def get_available_tts(self, user_id: str) -> GetAvailableProvidersResponse:
        """Get available TTS (Text-to-Speech) providers for a user.

        This method checks which TTS providers are available for the specified user
        based on their configured API keys. Providers that require no API keys
        (like zoetrope) are always available, while others require valid API keys
        to be configured in the user's profile.

        Args:
            user_id (str):
                Unique identifier of the user to check TTS availability for.

        Returns:
            GetAvailableProvidersResponse:
                Response containing a set of available TTS provider names.
        """
        tts_requirements = dict(
            zoetrope=set(),
            huoshan={'huoshan_app_id', 'huoshan_token'},
            huoshan_icl={'huoshan_app_id', 'huoshan_token'},
            softsugar={'softsugar_app_id', 'softsugar_app_key'},
            sensenova={'nova_tts_api_key'},
            elevenlabs={'elevenlabs_api_key'}
        )
        async with AsyncMongoClient(
                host=self.mongodb_host,
                port=self.mongodb_port,
                username=self.mongodb_username,
                password=self.mongodb_password,
                authSource=self.mongodb_auth_database,
        ) as client:
            db = client[self.mongodb_database]
            collection = db[self.mongodb_user_collection]
            api_keys = await collection.find_one(
                {"user_id": user_id},
                {"_id": 0})
        return_set = set()
        for key, value in tts_requirements.items():
            if len(value) == 0:
                return_set.add(key)
            elif all(api_keys.get(key) != '' for key in value):
                return_set.add(key)
        return GetAvailableProvidersResponse(options=return_set)

    async def _check_character_read_only(
            self,
            async_mongo_client: AsyncMongoClient,
            user_id: str,
            character_id: str) -> None:
        """Check if a character is read-only and raise exception if it is.

        Args:
            user_id (str):
                Unique identifier of the user.
            character_id (str):
                Unique identifier of the character.

        Raises:
            ReadOnlyCharacterException:
                If the character is marked as read-only.
        """
        db = async_mongo_client[self.mongodb_database]
        collection = db[self.mongodb_character_collection]
        character = await collection.find_one(
            {"user_id": user_id, "character_id": character_id},
            {"_id": 0, "read_only": 1}
        )
        if character and character.get("read_only", False):
            raise ReadOnlyCharacterException(
                status_code=403,
                detail="Character is read-only and cannot be modified"
            )

    async def _check_character_exists(
            self,
            async_mongo_client: AsyncMongoClient,
            user_id: str,
            character_id: str) -> None:
        """Check if a character exists and raise exception if it does not.

        This private method verifies that a character exists in the database
        for the specified user and character IDs.

        Args:
            async_mongo_client (AsyncMongoClient):
                MongoDB client for database operations.
            user_id (str):
                Unique identifier of the user.
            character_id (str):
                Unique identifier of the character.

        Raises:
            NoCharacterException:
                If the character is not found in the database.
        """
        db = async_mongo_client[self.mongodb_database]
        collection = db[self.mongodb_character_collection]
        character = await collection.find_one(
            {"user_id": user_id, "character_id": character_id},
            {"_id": 0}
        )
        if not character:
            msg = f"Character not found for user_id: {user_id} " +\
                f"and character_id: {character_id}."
            self.logger.error(msg)
            raise NoCharacterException(
                status_code=404,
                detail=msg)

    def root(self) -> RedirectResponse:
        """Redirect to API documentation.

        Returns:
            RedirectResponse: Redirect response to /docs endpoint.
        """
        return RedirectResponse(url="/docs")

    async def dowload_log_file(self) -> Response:
        """Download log file as attachment.

        This method retrieves the current log file and returns it
        as a downloadable attachment with appropriate headers.

        Returns:
            Response:
                Response containing the log file as attachment with
                Content-Disposition header set for download.

        Raises:
            NoLogFileException:
                If no log file is found or log path is not configured.
        """
        if self.log_path is None:
            msg = "No log file found."
            self.logger.error(msg)
            raise NoLogFileException(status_code=503, detail=msg)
        with open(self.log_path, "rb") as f:
            resp = Response(content=f.read(), media_type="application/octet-stream")
            base_name = os.path.basename(self.log_path)
            resp.headers["Content-Disposition"] = f"attachment; filename={base_name}"
            return resp

    async def tail_log(self, request: Request, n_lines: int) -> str:
        """Return the last n lines of the log file.

        This method reads the specified number of lines from the end
        of the log file and renders them in an HTML template for
        web display.

        Args:
            request (Request):
                FastAPI request object for template rendering.
            n_lines (int):
                Maximum number of lines to return from the end
                of the log file.

        Returns:
            str:
                Rendered HTML template containing the log content.

        Raises:
            NoLogFileException:
                If no log file is found or log path is not configured.
        """
        if self.log_path is None:
            msg = "No log file found."
            self.logger.error(msg)
            raise NoLogFileException(status_code=503, detail=msg)
        # read the last n_lines lines from the log file
        with open(self.log_path, encoding="utf-8") as f:
            lines = f.readlines()
            n_lines = min(int(n_lines), len(lines))
            log_content = "".join(lines[-n_lines:])
        # Render template and return
        return self.templates.TemplateResponse(
            "log_template.html", {"request": request, "log_content": log_content})


    async def health(self) -> JSONResponse:
        """Health check endpoint for service monitoring.

        This endpoint provides a simple health check that returns
        an 'OK' status to indicate the service is running properly.
        Used by load balancers and monitoring systems.

        Returns:
            JSONResponse:
                JSON response containing 'OK' status string.
        """
        resp = JSONResponse(content='OK')
        return resp

