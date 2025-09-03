from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Show(SQLModel, table=True):
    """TV Show model with global watch status"""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    watched: bool = Field(default=False)  # Global watch status
    rating: Optional[int] = Field(default=None, ge=1, le=5)  # Global rating
    watched_at: Optional[datetime] = Field(default=None)  # When it was watched


# Watch model removed - no longer needed for per-user tracking
