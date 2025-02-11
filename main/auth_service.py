# This is a placeholder.  Replace with your actual authentication logic.
# For example, you might have functions to verify JWT tokens and API keys
# against a database or other source of truth.

def verify_token(token: str) -> dict:
    """
    Verifies a JWT token.
    Replace this with your actual token verification logic.
    """
    valid_tokens = ["valid_token_123"]
    if token in valid_tokens:
        # Attach permission data as needed.
        return {"user_id": "123", "username": "testuser", "permission": "read_write"}
    else:
        return None

def verify_api_key(api_key: str) -> dict:
    """
    Verifies an API key.
    Replace this with your actual API key verification logic.
    """
    # Example: Check if the API key is in a database
    valid_api_keys = {"api_key_123": {"user_id": "456", "permission": "read_only"}}
    if api_key in valid_api_keys:
        return valid_api_keys[api_key]
    else:
        return None
