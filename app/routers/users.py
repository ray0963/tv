from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.db import SessionLocal
from app.models import Show, Watch
from app.schemas import WatchResponse, UnwatchedShowResponse
from app.auth import get_current_user

router = APIRouter()


def get_session():
    """Dependency to get database session"""
    with SessionLocal() as session:
        yield session


@router.get("/{username}/watched", response_model=List[WatchResponse])
async def get_user_watched_shows(
    username: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get watched shows for a specific user"""
    # Check if user exists (simple check against allowed users)
    from app.auth import ALLOWED_USERS

    if username not in ALLOWED_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get watched shows with ratings
    statement = (
        select(Show, Watch.rating, Watch.watched_at)
        .join(Watch, Show.id == Watch.show_id)
        .where(Watch.user == username)
    )

    results = session.exec(statement).all()

    watched_shows = []
    for result in results:
        if isinstance(result, tuple):
            show, rating, watched_at = result
            watched_shows.append(
                WatchResponse(
                    id=show.id, title=show.title, rating=rating, watched_at=watched_at
                )
            )

    return watched_shows


@router.get("/{username}/unwatched", response_model=List[UnwatchedShowResponse])
async def get_user_unwatched_shows(
    username: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get unwatched shows for a specific user"""
    # Check if user exists (simple check against allowed users)
    from app.auth import ALLOWED_USERS

    if username not in ALLOWED_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get unwatched shows (shows not in user's watch list)
    statement = select(Show).where(
        ~Show.id.in_(select(Watch.show_id).where(Watch.user == username))
    )

    unwatched_shows = session.exec(statement).all()

    return [
        UnwatchedShowResponse(id=show.id, title=show.title) for show in unwatched_shows
    ]
