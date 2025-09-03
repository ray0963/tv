from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.db import SessionLocal
from app.models import Show
from app.schemas import ShowCreate, ShowUpdate, ShowResponse, WatchCreate
from app.auth import get_current_user
from datetime import datetime

router = APIRouter()


def get_session():
    """Dependency to get database session"""
    with SessionLocal() as session:
        yield session


@router.get("/", response_model=List[ShowResponse])
async def list_shows(
    watched: Optional[bool] = Query(None, description="Filter by watched status"),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """List all shows with optional watched filter"""
    if watched is not None:
        # Filter by global watched status
        shows = session.exec(select(Show).where(Show.watched == watched)).all()
    else:
        # Return all shows
        shows = session.exec(select(Show)).all()

    return [
        ShowResponse(
            id=show.id,
            title=show.title,
            created_at=show.created_at,
            watched=show.watched,
            rating=show.rating,
            watched_at=show.watched_at,
        )
        for show in shows
    ]


@router.post("/", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
async def create_show(
    show_data: ShowCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Create a new TV show"""
    # Check for duplicate title
    existing_show = session.exec(
        select(Show).where(Show.title == show_data.title)
    ).first()

    if existing_show:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Show with this title already exists",
        )

    show = Show(title=show_data.title)
    session.add(show)
    session.commit()
    session.refresh(show)

    return ShowResponse(
        id=show.id,
        title=show.title,
        created_at=show.created_at,
        watched=show.watched,
        rating=show.rating,
        watched_at=show.watched_at,
    )


@router.patch("/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: int,
    show_data: ShowUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Update a TV show"""
    show = session.exec(select(Show).where(Show.id == show_id)).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Show not found"
        )

    # Check for duplicate title if updating title
    if show_data.title and show_data.title != show.title:
        existing_show = session.exec(
            select(Show).where(Show.title == show_data.title)
        ).first()

        if existing_show:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Show with this title already exists",
            )

    # Update fields
    if show_data.title is not None:
        show.title = show_data.title

    session.add(show)
    session.commit()
    session.refresh(show)

    return ShowResponse(
        id=show.id,
        title=show.title,
        created_at=show.created_at,
        watched=show.watched,
        rating=show.rating,
        watched_at=show.watched_at,
    )


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    show_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Delete a TV show"""
    show = session.exec(select(Show).where(Show.id == show_id)).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Show not found"
        )

    session.delete(show)
    session.commit()


@router.post("/{show_id}/watch", status_code=status.HTTP_201_CREATED)
async def watch_show(
    show_id: int,
    watch_data: WatchCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Mark a show as globally watched with rating"""
    # Validate rating
    if not 1 <= watch_data.rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5",
        )

    # Check if show exists
    show = session.exec(select(Show).where(Show.id == show_id)).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Show not found"
        )

    # Update global watch status
    show.watched = True
    show.rating = watch_data.rating
    show.watched_at = datetime.utcnow()

    session.add(show)
    session.commit()

    return {"message": "Show marked as globally watched"}


@router.delete("/{show_id}/watch", status_code=status.HTTP_204_NO_CONTENT)
async def unwatch_show(
    show_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Mark a show as globally unwatched"""
    # Check if show exists
    show = session.exec(select(Show).where(Show.id == show_id)).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Show not found"
        )

    # Update global watch status
    show.watched = False
    show.rating = None
    show.watched_at = None

    session.add(show)
    session.commit()
