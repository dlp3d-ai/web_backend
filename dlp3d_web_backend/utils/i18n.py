from typing import Any


def get_message(
        endpoint: str,
        key: str,
        messages: dict[str, dict[str, str]],
        language: str = 'en',
        **kwargs: Any) -> str:
    """Get localized message for a specific endpoint and key.

    This function retrieves a localized message from the messages dictionary
    based on the endpoint, key, and language. If the message template contains
    placeholders, they will be formatted using the provided keyword arguments.
    If the endpoint, language, or key is not found, appropriate fallback
    behavior is applied (returns the key itself or falls back to 'en' language).

    Args:
        endpoint (str):
            The endpoint name (e.g., 'authenticate_user', 'register_user').
            Used to locate the correct message group in the messages dictionary.
        key (str):
            The message key to retrieve (e.g., 'auth_error_incorrect_credentials').
            Used to locate the specific message within the endpoint's messages.
        messages (dict[str, dict[str, str]]):
            Nested dictionary containing all localized messages.
            Structure: {endpoint: {language: {key: message_template}}}.
            The message_template can contain placeholders like
            {field} or {error_message}.
        language (str, optional):
            Language code for the desired message (e.g., 'en', 'zh').
            If the specified language is not available, falls back to 'en'.
            Defaults to 'en'.
        **kwargs (Any):
            Additional keyword arguments used to format the message template.
            These arguments are passed to str.format() method.
            Common examples include 'field', 'message', 'error_message', 'user_id'.

    Returns:
        str:
            The localized and formatted message string. If the endpoint,
            language, or key is not found, returns the key itself. If template
            formatting fails due to missing arguments, returns the unformatted
            template string.
    """
    if endpoint not in messages:
        return key

    endpoint_messages = messages[endpoint]

    if language not in endpoint_messages:
        language = 'en'

    language_messages = endpoint_messages[language]

    if key not in language_messages:
        return key

    template = language_messages[key]

    try:
        return template.format(**kwargs)
    except KeyError:
        return template

