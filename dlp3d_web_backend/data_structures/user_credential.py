from pydantic import BaseModel


class UserCredential(BaseModel):
    """User credential model for authentication and user management.

    This model represents the basic authentication credentials for a user,
    including username, password, and the associated user ID. It is used
    for user registration, login authentication, and credential management
    operations in the system.

    Attributes:
        username (str):
            Unique username for the user account.
        password (str):
            User's password for authentication.
        user_id (str):
            Unique identifier for the user, typically a UUID.
    """
    username: str
    password: str
    user_id: str
