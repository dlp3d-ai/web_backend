from pydantic import BaseModel


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

class CreateUserRequest(BaseModel):
    """Request model for creating a new user with default configuration.

    This model contains the user ID for creating a new user account
    with default configuration and character settings.

    Attributes:
        user_id (str):
            Unique identifier for the user to be created.
    """
    user_id: str

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

    This model contains the necessary fields to delete a user.
    """
    user_id: str

class DuplicateCharacterRequest(BaseModel):
    """Request model for duplicating a character.

    This model contains the necessary fields to duplicate a character.
    """
    user_id: str
    character_id: str
    character_name: str | None = None

class DeleteCharacterRequest(BaseModel):
    """Request model for deleting a character.

    This model contains the necessary fields to delete a character.
    """
    user_id: str
    character_id: str

class UpdateCharacterNameRequest(BaseModel):
    """Request model for updating character name.

    This model contains the necessary fields to update a character's
    name.
    """
    user_id: str
    character_id: str
    character_name: str

class UpdateCharacterAvatarRequest(BaseModel):
    """Request model for updating character avatar.

    This model contains the necessary fields to update a character's
    avatar.
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
    """Request model for updating user API key configuration.

    This model contains all the API keys and authentication credentials
    for various AI services and third-party integrations. All fields
    are optional and default to None, allowing partial updates without
    affecting existing configurations.
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
