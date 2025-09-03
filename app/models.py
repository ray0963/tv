from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Show(SQLModel, table=True):
    """TV Show model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Watch(SQLModel, table=True):
    """User watch tracking model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user: str = Field(index=True)
    show_id: int = Field(foreign_key="show.id")
    rating: int = Field(ge=1, le=5)  # Rating 1-5
    watched_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Ensure unique combination of user and show
        table = True
