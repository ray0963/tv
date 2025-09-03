from app.models import Show, Watch
from app.db import SessionLocal
import os


def seed_demo_data():
    """Seed database with demo TV shows"""
    with SessionLocal() as session:
        # Check if data already exists
        existing_shows = session.query(Show).count()
        if existing_shows > 0:
            return  # Already seeded

        # Create demo shows
        demo_shows = [
            Show(title="Breaking Bad"),
            Show(title="The Wire"),
            Show(title="Mad Men"),
            Show(title="The Sopranos"),
            Show(title="Game of Thrones"),
        ]

        for show in demo_shows:
            session.add(show)

        session.commit()
        print("Demo data seeded successfully!")


def should_seed_data() -> bool:
    """Check if demo data should be seeded based on environment variable"""
    return os.getenv("SEED", "false").lower() == "true"
