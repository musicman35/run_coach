"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from runcoach.config import get_settings
from runcoach.routers import auth

settings = get_settings()

app = FastAPI(
    title="RunCoach AI",
    description="Personalized AI running coach",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
