from pydantic import BaseModel
from typing import Optional

# Pydantic model for the User
class UserSchema(BaseModel):
    name: str
    email: str
    nickname: Optional[str] = None

# Model for Token response (contains access token and token type)
class Token(BaseModel):
    access_token: str
    token_type: str

# Model for token data (used to extract user information from the token)
class TokenData(BaseModel):
    email: str
    # You can add more fields if needed (e.g. id, name, etc.)
