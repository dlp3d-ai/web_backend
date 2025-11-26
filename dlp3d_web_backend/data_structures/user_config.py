from pydantic import BaseModel


class UserConfig(BaseModel):
    """User configuration model for storing API keys and user settings.

    This model contains various API keys for different AI services and platforms,
    along with user-specific configuration such as timezone. All API key fields
    are optional and default to empty strings for security purposes.
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
    sensenovaomni_ak: str = ''
    sensenovaomni_sk: str = ''
    softsugar_app_id: str = ''
    softsugar_app_key: str = ''
    huoshan_app_id: str = ''
    huoshan_token: str = ''
    sense_tts_api_key: str = ''
    nova_tts_api_key: str = ''
    elevenlabs_api_key: str = ''
    timezone: str = 'Asia/Shanghai'
