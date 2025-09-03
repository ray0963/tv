from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routers import shows, users
from app.auth import verify_user, create_access_token
from app.schemas import UserLogin, Token
from app.utils import should_seed_data, seed_demo_data
import os

# Create FastAPI app
app = FastAPI(
    title="TV Show Tracker API",
    description="A simple API for tracking TV shows and user watch history",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # React default
        "*",  # Allow all in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(shows.router, prefix="/shows", tags=["shows"])
app.include_router(users.router, prefix="/users", tags=["users"])


# Auth endpoints
@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login with username and password"""
    if verify_user(user_credentials.username, user_credentials.password):
        access_token = create_access_token(data={"sub": user_credentials.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_credentials.username,
        }
    else:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TV Show Tracker API", "docs": "/docs", "users": ["ray", "dana"]}


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on startup"""
    # Initialize database
    init_db()

    # Seed demo data if enabled
    if should_seed_data():
        seed_demo_data()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
