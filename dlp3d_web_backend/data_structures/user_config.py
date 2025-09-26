from pydantic import BaseModel


class UserConfig(BaseModel):
    """User configuration model for API keys and service credentials.

    This model stores all the necessary API keys and authentication
    credentials for various AI services and third-party integrations
    that the user has configured. All API key fields default to empty
    strings and can be updated independently without affecting other
    service configurations.
    """
    user_id: str
    openai_api_key: str = ''
    xai_api_key: str = ''
    anthropic_api_key: str = ''
    gemini_api_key: str = ''
    deepseek_api_key: str = ''
    sensenova_api_key: str = ''
    sensenova_ak: str = ''
    sensenova_sk: str = ''
    softsugar_app_id: str = ''
    softsugar_app_key: str = ''
    huoshan_app_id: str = ''
    huoshan_token: str = ''
    sense_tts_api_key: str = ''
    nova_tts_api_key: str = ''
    elevenlabs_api_key: str = ''
