import base64
import hashlib
import hmac


def str_to_md5(input_str: str) -> str:
    """Convert a string to MD5 hash value.

    Args:
        input_str (str):
            Input string to be hashed.

    Returns:
        str:
            MD5 hash value as hexadecimal string.
    """
    hash_object = hashlib.md5()
    hash_object.update(input_str.encode('utf-8'))
    md5sum = hash_object.hexdigest()
    return md5sum

def get_secret_hash(username: str, client_id: str, secret_key: str) -> str:
    """Generate secret hash for AWS Cognito authentication using HMAC-SHA256.

    This function creates a secret hash required for AWS Cognito authentication
    by combining the username with the client ID and signing it with the secret
    key using HMAC-SHA256 algorithm.

    Args:
        username (str):
            Username for authentication.
        client_id (str):
            AWS Cognito application client ID.
        secret_key (str):
            AWS Cognito application client secret key.

    Returns:
        str:
            Base64-encoded secret hash for Cognito authentication.
    """
    message = bytes(username+client_id,'utf-8')
    key = bytes(secret_key,'utf-8')
    secret_hash = base64.b64encode(
            hmac.new(key, message, digestmod=hashlib.sha256
        ).digest()).decode()
    return secret_hash
