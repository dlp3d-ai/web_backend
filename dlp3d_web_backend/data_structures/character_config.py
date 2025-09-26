from pydantic import BaseModel


class CharacterConfig(BaseModel):
    """Character configuration model for AI character settings.

    This model defines the complete configuration for an AI character,
    including user identification, basic character information, adapter
    configurations for various AI services, and emotional/relationship
    threshold settings for character behavior.
    """
    user_id: str
    character_id: str
    character_name: str
    create_datatime: str
    read_only: bool = False
    scene_name: str
    tts_adapter: str
    voice: str
    voice_speed: float = 1.0
    avatar: str
    asr_adapter: str
    classification_adapter: str
    classification_model_override: str = ''
    conversation_adapter: str
    conversation_model_override: str = ''
    prompt: str
    reaction_adapter: str
    reaction_model_override: str = ''
    memory_adapter: str
    memory_model_override: str = ''
    acquaintance_threshold: int = 5
    friend_threshold: int = 10
    situationship_threshold: int = 15
    lover_threshold: int = 20
    neutral_threshold: int = 50
    happiness_threshold: int = 20
    sadness_threshold: int = 20
    fear_threshold: int = 20
    anger_threshold: int = 20
    disgust_threshold: int = 20
    surprise_threshold: int = 20
    shyness_threshold: int = 20

