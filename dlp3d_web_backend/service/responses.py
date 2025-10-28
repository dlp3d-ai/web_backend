from pydantic import BaseModel

from ..data_structures.character_config import CharacterConfig


class RegisterUserResponse(BaseModel):
    """Response model for user registration operation.

    This model contains the response data returned after successfully
    registering a new user account, including the generated user ID.

    Attributes:
        user_id (str):
            Unique identifier for the newly registered user.
        confirmation_required (bool):
            Whether the user needs to confirm their registration.
        auth_code (int):
            Authentication status code. Defaults to 200 for success.
        auth_msg (str):
            Authentication message providing additional information.
            Defaults to empty string.
    """
    user_id: str
    confirmation_required: bool
    auth_code: int = 200
    auth_msg: str = ""

class ConfirmRegistrationResponse(BaseModel):
    """Response model for user confirmation registration operation.

    This model contains the response data returned after successfully
    confirming a user's registration, including the authentication code and message.

    Attributes:
        auth_code (int):
            Authentication status code. Defaults to 200 for success.
        auth_msg (str):
            Authentication message providing additional information.
            Defaults to empty string.
    """
    auth_code: int = 200
    auth_msg: str = ""

class AuthenticateUserResponse(BaseModel):
    """Response model for user authentication operation.

    This model contains the response data returned after successfully
    authenticating a user, including the user ID for the authenticated user.

    Attributes:
        user_id (str):
            Unique identifier for the authenticated user.
        auth_code (int):
            Authentication status code. Defaults to 200 for success.
        auth_msg (str):
            Authentication message providing additional information.
            Defaults to empty string.
    """
    user_id: str
    auth_code: int = 200
    auth_msg: str = ""

class DeleteUserResponse(BaseModel):
    """Response model for user deletion operation.

    This model contains the response data returned after successfully
    deleting a user, including the user ID for the deleted user.

    Attributes:
        user_id (str):
            Unique identifier for the deleted user.
        auth_code (int):
            Authentication status code. Defaults to 200 for success.
        auth_msg (str):
            Authentication message providing additional information.
            Defaults to empty string.
    """
    user_id: str
    auth_code: int = 200
    auth_msg: str = ""


class UpdateUserPasswordResponse(BaseModel):
    """Response model for user password update operation.

    This model contains the response data returned after
    successfully updating a user's password at database.

    Attributes:
        confirmation_required (bool):
            Whether the user needs to confirm their password update.
        auth_code (int):
            Authentication status code. Defaults to 200 for success.
        auth_msg (str):
            Authentication message providing additional information.
            Defaults to empty string.
    """
    confirmation_required: bool
    auth_code: int = 200
    auth_msg: str = ""

class ListUsersResponse(BaseModel):
    """Response model for user list retrieval operation.

    This model contains the response data returned when fetching a list
    of users, including user IDs and optionally usernames.

    Attributes:
        user_id_list (list[str]):
            List of unique identifiers for all users.
        user_name_list (list[str] | None, optional):
            List of usernames corresponding to the user IDs.
            Defaults to None if usernames are not requested.
    """
    user_id_list: list[str]
    user_name_list: list[str] | None = None

class DuplicateCharacterResponse(BaseModel):
    """Response model for character duplication operation.

    This model contains the response data returned after successfully
    duplicating a character, including the new character ID.
    """
    character_id: str

class GetCharacterListResponse(BaseModel):
    """Response model for character list retrieval operation.

    This model contains the response data returned when fetching a list
    of characters for a specific user, including both character IDs and
    character names in corresponding order.
    """
    character_id_list: list[str]
    character_name_list: list[str]


class GetCharacterConfigResponse(CharacterConfig):
    """Response model for character configuration retrieval operation.

    This model inherits from CharacterConfig and contains the complete
    character configuration data returned when fetching a specific
    character's settings.
    """
    pass

class GetAvailableProvidersResponse(BaseModel):
    """Response model for available LLM services retrieval operation.

    This model contains the response data returned when checking which
    Large Language Model services are available for a user based on
    their configured API keys.
    """
    options: set[str]


class MeshV1Response(BaseModel):
    """Response model for mesh data.

    This model is used for WebSocket responses containing
    mesh data for avatars.
    """
    pass

class VersionV1Response(BaseModel):
    """Response model for version information.

    This model is used for WebSocket responses containing
    the current version of the motion file server.

    Args:
        version (str):
            Version string of the motion file server.
    """
    version: str

class MotionKeywordsV1Response(BaseModel):
    """Response model for motion keywords.

    This model is used for http responses containing
    the motion keywords.
    """
    motion_keywords: set[str]
