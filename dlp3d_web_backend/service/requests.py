from pydantic import BaseModel, EmailStr, Field


class RegisterUserRequest(BaseModel):
    """Request model for user registration.

    This model contains the necessary fields to register a new user
    account with username and password credentials.

    Attributes:
        username (str):
            Unique username for the new user account.
        password (str):
            Password for the new user account.
    """
    username: str
    password: str

class EmailAuthenticateUserRequest(BaseModel):
    """Request model for email-based user authentication.

    This model contains the necessary fields to authenticate a user
    using email address and password credentials. The email field is
    validated for proper email format, and the password must meet
    minimum length requirements.

    Attributes:
        username (EmailStr):
            Email address for authentication (validated for proper format).
        password (str):
            Password for authentication (minimum 8 characters required).
    """
    username: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long")

class ConfirmRegistrationRequest(BaseModel):
    """Request model for confirming user registration.

    This model contains the necessary fields to confirm a user's registration.

    Attributes:
        email (str):
            Email of the user to be confirmed.
        confirmation_code (str):
            Confirmation code for the user's registration.
    """
    email: EmailStr
    confirmation_code: str

class UpdateUserPasswordRequest(BaseModel):
    """Request model for updating user password.

    This model contains the necessary fields to update a user's password,
    including current credentials for authentication and the new password.

    Attributes:
        username (str):
            Username of the user whose password is being updated.
        password (str):
            Current password for authentication.
        new_password (str):
            New password to replace the current one.
    """
    username: str
    password: str
    new_password: str

class AuthenticateUserRequest(BaseModel):
    """Request model for user authentication.

    This model contains the credentials needed to authenticate a user
    and verify their identity for login operations.

    Attributes:
        username (str):
            Username for authentication.
        password (str):
            Password for authentication.
    """
    username: str
    password: str

class DeleteUserRequest(BaseModel):
    """Request model for deleting a user.

    This model contains the necessary fields to delete a user and all
    associated data from the system.

    Attributes:
        user_id (str):
            Unique identifier of the user to be deleted.
    """
    user_id: str

class DuplicateCharacterRequest(BaseModel):
    """Request model for duplicating a character.

    This model contains the necessary fields to create a copy of an
    existing character with optional name customization.

    Attributes:
        user_id (str):
            Unique identifier of the user who owns the character.
        character_id (str):
            Unique identifier of the character to duplicate.
        character_name (str | None, optional):
            Optional new name for the duplicated character. Defaults to None.
    """
    user_id: str
    character_id: str
    character_name: str | None = None

class DeleteCharacterRequest(BaseModel):
    """Request model for deleting a character.

    This model contains the necessary fields to permanently delete
    a character from the system.

    Attributes:
        user_id (str):
            Unique identifier of the user who owns the character.
        character_id (str):
            Unique identifier of the character to delete.
    """
    user_id: str
    character_id: str

class UpdateCharacterNameRequest(BaseModel):
    """Request model for updating character name.

    This model contains the necessary fields to update a character's
    display name in the system.

    Attributes:
        user_id (str):
            Unique identifier of the user who owns the character.
        character_id (str):
            Unique identifier of the character to update.
        character_name (str):
            New name for the character.
    """
    user_id: str
    character_id: str
    character_name: str

class UpdateCharacterAvatarRequest(BaseModel):
    """Request model for updating character avatar.

    This model contains the necessary fields to update a character's
    avatar image or visual representation.

    Attributes:
        user_id (str):
            Unique identifier of the user who owns the character.
        character_id (str):
            Unique identifier of the character to update.
        avatar (str):
            New avatar identifier or path for the character.
    """
    user_id: str
    character_id: str
    avatar: str

class UpdateCharacterSceneRequest(BaseModel):
    """Request model for updating character scene configuration.

    This model contains the necessary fields to update a character's
    scene configuration.
    """
    user_id: str
    character_id: str
    scene_name: str

class UpdateCharacterPromptRequest(BaseModel):
    """Request model for updating character prompt configuration.

    This model contains the necessary fields to update a character's
    system prompt, which defines the character's personality and
    behavior patterns.
    """
    user_id: str
    character_id: str
    prompt: str

class UpdateCharacterASRRequest(BaseModel):
    """Request model for updating character
    ASR (Automatic Speech Recognition) configuration.

    This model contains the necessary fields to update a character's
    speech recognition adapter settings.
    """
    user_id: str
    character_id: str
    asr_adapter: str

class UpdateCharacterTTSRequest(BaseModel):
    """Request model for updating character TTS (Text-to-Speech) configuration.

    This model contains the necessary fields to update a character's
    text-to-speech settings including adapter, voice selection, and
    speech speed parameters.
    """
    user_id: str
    character_id: str
    tts_adapter: str
    voice: str
    voice_speed: float = 1.0

class UpdateCharacterClassificationRequest(BaseModel):
    """Request model for updating character classification configuration.

    This model contains the necessary fields to update a character's
    emotion and intent classification settings, including adapter
    selection and optional model overrides.
    """
    user_id: str
    character_id: str
    classification_adapter: str
    classification_model_override: str = ''

class UpdateCharacterConversationRequest(BaseModel):
    """Request model for updating character conversation configuration.

    This model contains the necessary fields to update a character's
    conversation handling settings, including adapter selection and
    optional model overrides for dialogue generation.
    """
    user_id: str
    character_id: str
    conversation_adapter: str
    conversation_model_override: str = ''

class UpdateCharacterReactionRequest(BaseModel):
    """Request model for updating character reaction configuration.

    This model contains the necessary fields to update a character's
    reaction generation settings, including adapter selection and
    optional model overrides for emotional responses.
    """
    user_id: str
    character_id: str
    reaction_adapter: str
    reaction_model_override: str = ''

class UpdateCharacterMemoryRequest(BaseModel):
    """Request model for updating character memory configuration.

    This model contains the necessary fields to update a character's
    memory management settings, including adapter selection and
    optional model overrides for memory storage and retrieval.
    """
    user_id: str
    character_id: str
    memory_adapter: str
    memory_model_override: str = ''

class UpdateUserConfigRequest(BaseModel):
    """Request model for updating user API key and settings configuration.

    This model contains all the API keys and user settings for various AI services
    and third-party integrations, including timezone configuration. All fields
    are optional and default to None, allowing partial updates without affecting
    existing configurations.
    """
    user_id: str
    openai_api_key: str | None = None
    xai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    deepseek_api_key: str | None = None
    sensenova_api_key: str | None = None
    sensenova_ak: str | None = None
    sensenova_sk: str | None = None
    softsugar_app_id: str | None = None
    softsugar_app_key: str | None = None
    huoshan_app_id: str | None = None
    huoshan_token: str | None = None
    sense_tts_api_key: str | None = None
    nova_tts_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    timezone: str | None = None


class VersionV1Request(BaseModel):
    """Request model for getting motion file version information.

    This model is used for WebSocket requests to retrieve the current
    version of the motion file server.
    """
    pass

class RestposeV1Request(BaseModel):
    """Request model for getting restpose data.

    This model is used for WebSocket requests to retrieve restpose
    information for a specific avatar.

    Args:
        avatar (str):
            Name of the avatar to get restpose data for.
    """
    avatar: str

class MeshV1Request(BaseModel):
    """Request model for getting mesh data.

    This model is used for WebSocket requests to retrieve mesh
    data for a specific avatar.

    Args:
        avatar (str):
            Name of the avatar to get mesh data for.
    """
    avatar: str

class JointsMetaV1Request(BaseModel):
    """Request model for getting joints meta data.

    This model is used for WebSocket requests to retrieve joints
    metadata for a specific avatar.

    Args:
        avatar (str):
            Name of the avatar to get joints metadata for.
    """
    avatar: str

class RigidsMetaV1Request(BaseModel):
    """Request model for getting rigids meta data.

    This model is used for WebSocket requests to retrieve rigids
    metadata for a specific avatar.

    Args:
        avatar (str):
            Name of the avatar to get rigids metadata for.
    """
    avatar: str

class BlendshapesMetaV1Request(BaseModel):
    """Request model for getting blendshapes meta data.

    This model is used for WebSocket requests to retrieve blendshapes
    metadata for a specific avatar.

    Args:
        avatar (str):
            Name of the avatar to get blendshapes metadata for.
    """
    avatar: str

class MotionFileV1Request(BaseModel):
    """Request model for getting motion file data.

    This model is used for WebSocket requests to retrieve motion
    file data for a specific avatar and application.

    Args:
        avatar (str):
            Name of the avatar to get motion data for.
        app_name (str):
            Target application name for the motion data.
    """
    avatar: str
    app_name: str
