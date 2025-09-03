from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.db import SessionLocal
from app.models import Show, Watch
from app.schemas import ShowCreate, ShowUpdate, ShowResponse, WatchCreate
from app.auth import get_current_user

router = APIRouter()


def get_session():
    """Dependency to get database session"""
    with SessionLocal() as session:
        yield session


@router.get("/", response_model=List[ShowResponse])
async def list_shows(
    watched: Optional[bool] = Query(
        None, description="Filter by watched status for current user"
    ),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """List all shows with optional watched filter"""
    if watched is not None:
        # Filter by watched status for current user
        if watched:
            # Get watched shows
            statement = (
                select(Show, Watch.rating, Watch.watched_at)
                .join(Watch, Show.id == Watch.show_id)
                .where(Watch.user == current_user)
            )
        else:
            # Get unwatched shows
            statement = select(Show).where(
                ~Show.id.in_(select(Watch.show_id).where(Watch.user == current_user))
            )

        results = session.exec(statement).all()

        if watched:
            # Format watched shows
            shows = []
            for result in results:
                if isinstance(result, tuple):
                    show, rating, watched_at = result
                    shows.append(
                        ShowResponse(
                            id=show.id,
                            title=show.title,
                            created_at=show.created_at,
                            watched=True,
                            rating=rating,
                        )
                    )
                else:
                    shows.append(
                        ShowResponse(
                            id=result.id,
                            title=result.title,
                            created_at=result.created_at,
                            watched=False,
                        )
                    )
            return shows
        else:
            # Format unwatched shows
            return [
                ShowResponse(
                    id=show.id,
                    title=show.title,
                    created_at=show.created_at,
                    watched=False,
                )
                for show in results
            ]
    else:
        # Return all shows with watched status for current user
        shows = session.exec(select(Show)).all()
        result = []

        for show in shows:
            # Check if user has watched this show
            watch = session.exec(
                select(Watch).where(
                    Watch.show_id == show.id, Watch.user == current_user
                )
            ).first()

            result.append(
                ShowResponse(
                    id=show.id,
                    title=show.title,
                    created_at=show.created_at,
                    watched=watch is not None,
                    rating=watch.rating if watch else None,
                )
            )

        return result


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

    return ShowResponse(id=show.id, title=show.title, created_at=show.created_at)


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

    return ShowResponse(id=show.id, title=show.title, created_at=show.created_at)


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

    # Delete associated watches first
    session.exec(select(Watch).where(Watch.show_id == show_id)).delete()

    session.delete(show)
    session.commit()


@router.post("/{show_id}/watch", status_code=status.HTTP_201_CREATED)
async def watch_show(
    show_id: int,
    watch_data: WatchCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Mark a show as watched with rating"""
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

    # Check if already watched
    existing_watch = session.exec(
        select(Watch).where(Watch.show_id == show_id, Watch.user == current_user)
    ).first()

    if existing_watch:
        # Update existing watch
        existing_watch.rating = watch_data.rating
        existing_watch.watched_at = Watch.watched_at.default_factory()
        session.add(existing_watch)
    else:
        # Create new watch
        watch = Watch(user=current_user, show_id=show_id, rating=watch_data.rating)
        session.add(watch)

    session.commit()
    return {"message": "Show marked as watched"}


@router.delete("/{show_id}/watch", status_code=status.HTTP_204_NO_CONTENT)
async def unwatch_show(
    show_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Mark a show as unwatched"""
    # Check if show exists
    show = session.exec(select(Show).where(Show.id == show_id)).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Show not found"
        )

    # Delete watch record
    watch = session.exec(
        select(Watch).where(Watch.show_id == show_id, Watch.user == current_user)
    ).first()

    if watch:
        session.delete(watch)
        session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show not marked as watched by this user",
        )
