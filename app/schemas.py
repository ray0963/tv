from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Auth schemas
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: str

# Show schemas
class ShowCreate(BaseModel):
    title: str

class ShowUpdate(BaseModel):
    title: Optional[str] = None

class ShowResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    watched: bool
    rating: Optional[int] = None
    watched_at: Optional[datetime] = None

# Watch schemas (now global)
class WatchCreate(BaseModel):
    rating: int

class WatchResponse(BaseModel):
    id: int
    title: str
    rating: int
    watched_at: datetime

# Remove UnwatchedShowResponse - no longer needed
