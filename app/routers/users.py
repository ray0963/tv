from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.db import SessionLocal
from app.models import Show
from app.schemas import ShowResponse
from app.auth import get_current_user

router = APIRouter()


def get_session():
    """Dependency to get database session"""
    with SessionLocal() as session:
        yield session


@router.get("/{username}/watched", response_model=List[ShowResponse])
async def get_user_watched_shows(
    username: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get globally watched shows (same for all users now)"""
    # Check if user exists (simple check against allowed users)
    from app.auth import ALLOWED_USERS

    if username not in ALLOWED_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get all globally watched shows
    watched_shows = session.exec(select(Show).where(Show.watched == True)).all()

    return [
        ShowResponse(
            id=show.id,
            title=show.title,
            created_at=show.created_at,
            watched=show.watched,
            rating=show.rating,
            watched_at=show.watched_at,
        )
        for show in watched_shows
    ]


@router.get("/{username}/unwatched", response_model=List[ShowResponse])
async def get_user_unwatched_shows(
    username: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get globally unwatched shows (same for all users now)"""
    # Check if user exists (simple check against allowed users)
    from app.auth import ALLOWED_USERS

    if username not in ALLOWED_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get all globally unwatched shows
    unwatched_shows = session.exec(select(Show).where(Show.watched == False)).all()

    return [
        ShowResponse(
            id=show.id,
            title=show.title,
            created_at=show.created_at,
            watched=show.watched,
            rating=show.rating,
            watched_at=show.watched_at,
        )
        for show in unwatched_shows
    ]
