from pydantic import BaseModel

from ..data_structures.character_config import CharacterConfig


class RegisterUserResponse(BaseModel):
    """Response model for user registration operation.

    This model contains the response data returned after successfully
    registering a new user account, including the generated user ID.

    Attributes:
        user_id (str):
            Unique identifier for the newly registered user.
    """
    user_id: str

class AuthenticateUserResponse(BaseModel):
    """Response model for user authentication operation.

    This model contains the response data returned after successfully
    authenticating a user, including the user ID for the authenticated user.

    Attributes:
        user_id (str):
            Unique identifier for the authenticated user.
    """
    user_id: str

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

