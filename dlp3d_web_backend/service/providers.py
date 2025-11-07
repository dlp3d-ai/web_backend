"""Provider requirements configuration for API key management.

This module defines the API key requirements for different service providers
used in the system, including Large Language Model (LLM), Automatic Speech
Recognition (ASR), and Text-to-Speech (TTS) services.
"""

LLM_REQUIREMENTS = dict(
    openai={'openai_api_key'},
    xai={'xai_api_key'},
    anthropic={'anthropic_api_key'},
    gemini={'gemini_api_key'},
    deepseek={'deepseek_api_key'},
    sensenova={'sensenova_ak', 'sensenova_sk'},
)

ASR_REQUIREMENTS = dict(
    openai={'openai_api_key'},
    zoetrope=set(),
    softsugar={'softsugar_app_id', 'softsugar_app_key'}
)

TTS_REQUIREMENTS = dict(
    zoetrope=set(),
    huoshan={'huoshan_app_id', 'huoshan_token'},
    huoshan_icl={'huoshan_app_id', 'huoshan_token'},
    softsugar={'softsugar_app_id', 'softsugar_app_key'},
    sensenova={'nova_tts_api_key'},
    elevenlabs={'elevenlabs_api_key'}
)
