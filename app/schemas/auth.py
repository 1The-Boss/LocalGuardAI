from pydantic import BaseModel
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    leader = "leader"
    citizen = "citizen"

class UserLogin(BaseModel):
    username: str
    password: str



class Token(BaseModel):
    access_token: str
    # token_type: str
    # role: UserRole

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None